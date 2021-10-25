#!/usr/bin/env python3

# ============================================================================
#
#   Author : --- WoodyTheWoo ---
#
#   inst_ERASynthMicro.py
#
#   Python module to talk to ERASynth Micro instrument.
#   Using the USB cable and serial communication.
#
#   Version   	Date            Modification
#
#   1.0         14/04/2021      Initial version
#
#   1.1         22/04/2021      Added last missing commands.
#                               Commands from document "COMMAND LIST"
#                               on November 2019 + added logging
#
#	1.2			13/10/2021		Translated to English
#
# ============================================================================


import sys
import serial
import time
import logging as log


__version = '1.2'
__date__ = '2021-04-14'
__updated__ = '2021-10-13'


# ===============================================
#   Handling class for ERA Synth Micro instrument
# ===============================================
class InstERASynthMicro:

    __SEND_DELAY = 0.1  # 100ms tempo as some breathing room for sending the command over serial
    __EOL = b'\r'  # Commands ended with a CR, encoded as binary

    # ===========================================
    #   Init
    # ===========================================
    def __init__(self, port='/dev/ttyACM0'):
        """
        Init, with args :
            . COM Port Baud Rate: 9600 bps.
            . Connection must be made with RTS/CTS flow control.
            . All commands have to be sent with carriage return.
        """
        try:
            self.__serial_link = serial.Serial(port=port, baudrate=9600, timeout=1, rtscts=True, xonxoff=True)
        except serial.SerialException:
            log.error(f'ERROR: Unable to open serial port {port}')
            sys.exit()

    # ===========================================
    #   Del
    # ===========================================
    def __del__(self):
        self.__serial_link.close()

    # ==========================================================
    #   Send commands over serial line
    # ==========================================================
    def __send_cmd(self, cmd):
        """
        Sends ONE command
        String encoded as binary, ended with CR
        """
        self.__serial_link.write(cmd.encode() + self.__EOL)
        self.__serial_link.flush()
        time.sleep(self.__SEND_DELAY)

    def __send_cmd_resp(self, cmd):
        """
        Sends ONE command, with response
        Return the response as a string
        """
        self.__serial_link.write(cmd.encode() + self.__EOL)
        self.__serial_link.flush()
        resp = self.__serial_link.readline().decode()
        resp_clean = resp.strip()
        return resp_clean.strip()

    # ===========================================
    #   Output ON and OFF commands on instrument
    # ===========================================
    def set_rf_on(self):
        self.__send_cmd('>SF1')
        log.info('Synth ON')
        self.refresh_lcd_home()  # Force screen refresh

    def set_rf_off(self):
        self.__send_cmd('>SF0')
        log.info('Synth OFF')
        self.refresh_lcd_home()  # Force screen refresh

    # ===========================================
    #   Screen refresh
    # ===========================================
    """ 
    Attention, *** Send these commands according to current page on LCD.
                Different page commands will cause abnormal behavior. ***
    """
    def refresh_lcd_home(self):
        self.__send_cmd('>GH')  # Refresh HOME screen only

    # ======================================================================
	#	Convert numerical value (frequency, time, etc) in string
	# 	format to be send on serial line
    # ======================================================================
    @staticmethod
    def __num_to_str(freq):
        if type(freq) == float:
            return str(int(freq))
        elif type(freq) == int:
            return str(freq)
        elif type(freq) == str:
            return '0'  # TODO Implement SI unit parser eg. '1k' -> 1000 / '3.2G' -> 3200000000
        else:
            return '0'

    # ========================================================================
    #   Define frequency (in Hz) and amplitude (in dBm)
    # ========================================================================
    def set_frequency(self, freq=1e9):
        """
        In Hertz.
        From docs :
            freq should be replaced by an integer number
            e.g. >F100000000 sets 100 MHz.
        """
        self.__send_cmd('>F' + self.__num_to_str(freq))
        log.info(f'Frequency set to {freq} Hz')
        self.refresh_lcd_home()

    def set_amplitude(self, ampl=0):
        """
        In dBm.
        From docs :
            ampl should be replaced by a decimal number
            e.g. >A-15 sets -15 dBm. Resolution is 1 dB.
        """
        self.__send_cmd('>SA' + str(ampl))
        log.info(f'Amplitude set to {ampl} dBm')
        self.refresh_lcd_home()

    # ======================================================================================
    #   Define modulation parameters
    # ======================================================================================
    def set_modulation_on(self):
        self.__send_cmd('>SM1')
        log.info(f'Modulation ON')
        self.refresh_lcd_home()

    def set_modulation_off(self):
        self.__send_cmd('>SM0')
        log.info(f'Modulation OFF')
        self.refresh_lcd_home()

    def set_modulation_source_internal(self):
        self.__send_cmd('>SMI0')
        log.info(f'Modulation source set to INTERNAL')
        self.refresh_lcd_home()

    def set_modulation_source_external(self):
        self.__send_cmd('>SMI1')
        log.info(f'Modulation source set to EXTERNAL')
        self.refresh_lcd_home()

    def set_modulation_source_microphone(self):
        self.__send_cmd('>SMI2')
        log.info(f'Modulation source set to MICROPHONE')
        self.refresh_lcd_home()

    def set_modulation_source(self, source='Internal'):
        if source.lower() in ['internal', 'int']:
            self.set_modulation_source_internal()
        elif source.lower() in ['external', 'ext']:
            self.set_modulation_source_external()
        elif source.lower() in ['microphone', 'mic']:
            self.set_modulation_source_microphone()
        else:
            log.warning(f'Modulation source not set, incorrect source: {source.lower()}')
            pass
        self.refresh_lcd_home()

    def set_modulation_type_am(self):
        self.__send_cmd('>SMT0')
        log.info(f'Modulation type set to AM')
        self.refresh_lcd_home()

    def set_modulation_type_fm(self):
        self.__send_cmd('>SMT1')
        log.info(f'Modulation type set to FM')
        self.refresh_lcd_home()

    def set_modulation_type_pulse(self):
        self.__send_cmd('>SMT2')
        log.info(f'Modulation type set to PULSE')
        self.refresh_lcd_home()

    def set_modulation_type(self, mod_type='AM'):
        if mod_type.lower() in ['am', 'amplitude']:
            self.set_modulation_type_am()
        elif mod_type.lower() in ['fm', 'frequency']:
            self.set_modulation_type_fm()
        elif mod_type.lower() in ['pulse']:
            self.set_modulation_type_pulse()
        else:
            log.warning(f'Modulation type not set, incorrect type: {mod_type.lower()}')
            pass
        self.refresh_lcd_home()

    def set_modulation_wave_sine(self):
        self.__send_cmd('>SMW0')
        log.info(f'Modulation wave type set to SINE')
        self.refresh_lcd_home()

    def set_modulation_wave_ramp(self):
        self.__send_cmd('>SMW1')
        log.info(f'Modulation wave type set to RAMP')
        self.refresh_lcd_home()

    def set_modulation_wave_square(self):
        self.__send_cmd('>SMW2')
        log.info(f'Modulation wave type set to SQUARE')
        self.refresh_lcd_home()

    def set_modulation_wave_triangle(self):
        self.__send_cmd('>SMW0')
        log.info(f'Modulation wave type set to TRIANGLE')
        self.refresh_lcd_home()

    def set_modulation_wave_type(self, wave='Sine'):
        if wave.lower() in ['sine']:
            self.set_modulation_wave_sine()
        elif wave.lower() in ['ramp']:
            self.set_modulation_wave_ramp()
        elif wave.lower() in ['square']:
            self.set_modulation_wave_square()
        elif wave.lower() in ['triangle']:
            self.set_modulation_wave_triangle()
        else:
            log.warning(f'Modulation wave type not set, incorrect wave: {wave.lower()}')
            pass
        self.refresh_lcd_home()

    def set_modulation_frequency(self, freq=1e3):
        self.__send_cmd('>SMF' + self.__num_to_str(freq))
        log.info(f'Internal modulation frequency set to {freq} Hz')
        self.refresh_lcd_home()

    def set_modulation_am_depth(self, depth=20):
        self.__send_cmd('>SMA' + str(depth))
        log.info(f'AM modulation depth set to {depth}%')
        self.refresh_lcd_home()

    def set_modulation_fm_deviation(self, deviation=1e3):
        self.__send_cmd('>SMFD' + self.__num_to_str(deviation))
        log.info(f'FM deviation set to {deviation} Hz')
        self.refresh_lcd_home()

    def set_modulation_pulse_period_us(self, period=1e3):
        self.__send_cmd('>SMPP' + self.__num_to_str(period))
        log.info(f'Pulse modulation period set to {period} µs')
        self.refresh_lcd_home()

    def set_modulation_pulse_width_us(self, width=2e3):
        self.__send_cmd('>SMPW' + self.__num_to_str(width))
        log.info(f'Pulse modulation width set to {width} µs')
        self.refresh_lcd_home()

    # ======================================================================================
    #   Define sweep parameters
    # ======================================================================================
    def set_sweep_on(self):
        self.__send_cmd('>SS5')
        log.info(f'Sweep ON')
        self.refresh_lcd_home()

    def set_sweep_off(self):
        self.__send_cmd('>SS6')
        log.info(f'Sweep OFF')
        self.refresh_lcd_home()

    def set_sweep_trigger_freerun(self):
        self.__send_cmd('>SS70')
        log.info(f'Sweep trigger set to FREERUN')
        self.refresh_lcd_home()

    def set_sweep_trigger_external(self):
        self.__send_cmd('>SS71')
        log.info(f'Sweep trigger set to EXTERNAL')
        self.refresh_lcd_home()

    def set_sweep_trigger(self, trigger='free'):
        if trigger.lower() in ['free', 'freerun']:
            self.set_sweep_trigger_freerun()
        elif trigger.lower() in ['ext', 'external']:
            self.set_sweep_trigger_external()
        else:
            log.warning(f'Sweep trigger not set, incorrect type: {trigger.lower()}')
            pass
        self.refresh_lcd_home()

    def set_sweep_start_frequency(self, freq=100e6):
        self.__send_cmd('>SS1' + self.__num_to_str(freq))
        log.info(f'Sweep START frequency set to {freq} Hz')
        self.refresh_lcd_home()

    def set_sweep_stop_frequency(self, freq=200e6):
        self.__send_cmd('>SS2' + self.__num_to_str(freq))
        log.info(f'Sweep STOP frequency set to {freq} Hz')
        self.refresh_lcd_home()

    def set_sweep_step_frequency(self, freq=1e6):
        self.__send_cmd('>SS3' + self.__num_to_str(freq))
        log.info(f'Sweep STEP frequency set to {freq} Hz')
        self.refresh_lcd_home()

    def set_sweep_dwell_time_us(self, dwell=1e3):
        self.__send_cmd('>SS4' + self.__num_to_str(dwell))
        log.info(f'Sweep DWELL time set to {dwell} µs')
        self.refresh_lcd_home()

    # ======================================================================================
    #   Define reference source
    # ======================================================================================
    def set_ref_source_internal(self):
        self.__send_cmd('>SR0')
        log.info(f'Reference source set on INTERNAL')
        self.refresh_lcd_home()

    def set_ref_source_external(self):
        self.__send_cmd('>SR1')
        log.info(f'Reference source set on EXTERNAL')
        self.refresh_lcd_home()

    def set_ref_source(self, source='Internal'):
        if source.lower() in ['internal', 'int']:
            self.set_ref_source_internal()
        elif source.lower() in ['external', 'ext']:
            self.set_ref_source_external()
        else:
            log.warning(f'Reference source not set, incorrect source: {source.lower()}')
            pass
        self.refresh_lcd_home()

    # ======================================================================================
    #   Vibrations preferences
    # ======================================================================================
    def set_vibration_on(self):
        """
        Power ON vibration
        """
        self.__send_cmd('>SV1')
        log.info(f'Vibration ON')
        self.refresh_lcd_home()

    def set_vibration_off(self):
        """
        Power OFF vibration
        """
        self.__send_cmd('>SV0')
        log.info(f'Vibration OFF')
        self.refresh_lcd_home()

    def set_vibration(self, vibration='on'):
        """
        Additional method to set ON/OFF vibrations on instrument
        """
        if vibration.lower() in ['on']:
            self.set_vibration_on()
        elif vibration.lower() in ['off']:
            self.set_vibration_off()
        else:
            log.warning(f'Vibration setting not set, incorrect option: {vibration.lower()}')

    def vibrate_30ms(self):
        """
        Activate a 30ms vibration
        """
        self.__send_cmd('>GV')
        log.info(f'Vibrate synth for 30ms ...bzz...')

    # ======================================================================================
    #   Preset instrument
    # ======================================================================================
    def set_preset(self):
        """
        Define instrument preset parameters :
         . Output RF OFF
         . Frequency 100MHz
         . Amplitude 0dBm
         . No modulation
         . No sweep
         . Internal source
         ! No reset on modulation and sweep parameters !
        """
        self.set_rf_off()
        self.set_frequency()
        self.set_amplitude()
        self.set_modulation_off()
        self.set_sweep_off()
        self.set_ref_source_internal()
        self.refresh_lcd_home()

    # ======================================================================================
    #   Reading temperature and current informations from instrument
    # ======================================================================================
    def get_temperature(self):
        """
        Give back temperature information, in °C
        """
        data = self.__send_cmd_resp('>RT')
        return data

    def get_current(self):
        """
        Give back current information, in Amps
        """
        data = self.__send_cmd_resp('>RC')
        return data


# ===========================================
#   Class tester - Basics functions
# ===========================================
if __name__ == '__main__':
    log.basicConfig(level=log.INFO)

    synth = InstERASynthMicro()  # Init serial line
    synth.set_preset()

    synth.set_rf_off()  # Synth OFF
    synth.set_amplitude(0)
    synth.set_frequency(1e9)
    synth.set_rf_on()
    input()
    synth.set_modulation_type_am()
    synth.set_modulation_source('int')
    synth.set_modulation_frequency(100e6)
    synth.set_modulation_am_depth(20)
    synth.set_modulation_wave_triangle()
    synth.set_modulation_on()
    input()
    synth.set_modulation_off()
    synth.set_modulation_wave_sine()
    synth.set_modulation_am_depth(50)
    synth.set_modulation_on()
    input()
    synth.set_modulation_off()
    synth.set_modulation_type_fm()
    synth.set_modulation_on()
    input()

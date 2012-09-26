/*
	Creative Machines Lab Aracna Firmware
	aracna.c - Main Program File
	Copyright (c) Creative Machines Lab, Cornell University, 2012 - http://www.creativemachines.org
	Authored by Jeremy Blum - http://www.jeremyblum.com

	LICENSE: GPLv3
	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

/** FIRMWARE REVISION  		*/
	#define FIRMWARE_VERSION 0x01
	
/** HARDWARE CONFIGURATION	*/
	#define NUM_MOTORS	8

#ifndef F_CPU
#define F_CPU 16000000UL
#endif

/** INCLUDE AVR HEADERS 	*/
#include <avr/io.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <util/delay.h>

/** INCLUDE PROGRAM HEADERS */
#include "aracna.h"
#include "macros.h"
#include "ax12.h"
#include "uart.h"

// UART Configuration and Buffers
// putchar and getchar are in uart.c
//FILE uart_str = FDEV_SETUP_STREAM(uart_putchar, uart_getchar, _FDEV_SETUP_RW); 
	#define SERIAL_STRING_LENGTH 60				//Input String Length
	char input[SERIAL_STRING_LENGTH];			//complete input string
	uint16_t vals[NUM_MOTORS] = {0};			//For holding the values that come over serial for each of our servos
	char cmd; 									//the command character


// making these volatile keeps the compiler from optimizing loops of available()
volatile int ax_rx_Pointer;
volatile int ax_tx_Pointer;
volatile int ax_rx_int_Pointer;


/** Main program entry point. This routine contains the overall program flow
 */
int main(void)
{
	initialize(); 	//Configures Ports, sets default values, etc.

	//Loop Forever
	for (;;)
	{
		//we add data starting with an '.' to the buffer until we get the newline character.
		fgets(input, sizeof(input), stdin); 	//Get the actual input (reads up to and including newline character)
		cmd = input[1]; 						//command char is always the first char of the input data after the '.'
		
		//Command = 'q' - Query for the current status
		if (cmd == 'q')
		{
			memset(input, 0, sizeof(input)); 							//Clear previous input
			fprintf(stdout, ".q%d,%d\n",   FIRMWARE_VERSION, NUM_MOTORS);  			//ACK w/ Firmware Version, # of Motors
		}
		
		//Command = 'l' - Command to Control Debug LED
		else if (cmd == 'l')
		{
			if (input[2] == '1')		DEBUG_LED_ON();					//Turn LED On
			else if (input[2] == '0')	DEBUG_LED_OFF();				//Turn LED Off
			memset(input, 0, sizeof(input)); 							//Clear previous input
			fprintf(stdout, ".l%d\n", DEBUG_LED_STATE());				//ACK		
		}
		
		//Command = 'v' - Sets all motor speeds
		//Comma separated entries telling all motors to set certain speeds
		//Assumes motor IDs are 0 <-> NUM_MOTORS-1
		else if (cmd == 'v')
		{
			parse_serial();						//Read the input string to an array of values
			memset(input, 0, sizeof(input)); 	//Clear previous input
			
			//send those speed commands
			for (int i = 0; i<NUM_MOTORS; i++)
			{
				ax12SetRegister2(i, AX_GOAL_SPEED_L, vals[i]);
			}
			_delay_ms(25);
			//Only after we have commanded all the speeds, can we check the status
			fprintf(stdout, ".v");														//ACK Character
			
			//Send ACK Info
			for (int i = 0; i<NUM_MOTORS; i++)
			{
				fprintf(stdout, "%d", ax12GetRegister(i, AX_GOAL_SPEED_L, 2));	//Return velocity setting
				if (i<NUM_MOTORS-1) fprintf(stdout, ",");								//Print delimiter
			}
			
			fprintf(stdout, "\n");														//ACK Newline
		}
		
		//Command = 'c' - Command all the motors to a new position
		//Comma separated entries telling all motors to move to positions from 0-1023
		//Assumes motor IDs are 0 <-> NUM_MOTORS-1
		else if (cmd == 'c')
		{
			parse_serial();						//Read the input string to an array of positions
			memset(input, 0, sizeof(input)); 	//Clear previous input
			
			//send those position commands
			for (int i = 0; i<NUM_MOTORS; i++)
			{
				ax12SetRegister2(i, AX_GOAL_POSITION_L, vals[i]);
			}
			
			//Only after we have commanded all the positions, can we check the status
			fprintf(stdout, ".c");														//ACK Character
			
			//Send ACK Info
			for (int i = 0; i<NUM_MOTORS; i++)
			{
				while(ax12GetRegister(i,AX_MOVING,1));									//Wait for this motor to finish moving
				fprintf(stdout, "%d", ax12GetRegister(i, AX_PRESENT_POSITION_L, 2));	//Return the present position
				if (i<NUM_MOTORS-1) fprintf(stdout, ",");								//Print delimiter
			}				
			
			fprintf(stdout, "\n");														//ACK Newline
		}
	}

}

/** initialize()
	Sets up the UARTS, configures pin directions, says hello, then blinks at you.
*/
void initialize(void)
{
	//init the UART0 to the Computer
	uart_init();
	stdout = &uart_output;
	stdin  = &uart_input;
	
	//Initialize the AX12 UART1
	ax12Init(1000000);
	
	//Initialize Pin Directions and States for I/O
	DDRB |= (DEBUG_LED_NUM);
	DEBUG_LED_OFF();

	//We're live.  Say Hello
	fprintf(stdout,".h\n");
	
	//Blink The Board LED and all Dynamixel LEDs to show We're good to go
	for (int i = 0; i<NUM_MOTORS; i++) ax12SetRegister(i, AX_LED, 0);
	DEBUG_LED_OFF();
	_delay_ms(500);
	for (int i = 0; i<NUM_MOTORS; i++) ax12SetRegister(i, AX_LED, 1);
	DEBUG_LED_ON();
	_delay_ms(500);
	for (int i = 0; i<NUM_MOTORS; i++) ax12SetRegister(i, AX_LED, 0);
	DEBUG_LED_OFF();
	
	
	
}

/** parse_serial()
	Assumes the input buffer has been populated with data of this form: ".c<val0>,<val1>,<val2>,...<val7>\n" as a char array
	This function reads this buffer, and populates the "vals" array with the integer representations of 10-bit values for each motor command
*/
void parse_serial(void)
{
	for (uint8_t i = 0; i < NUM_MOTORS; i++) vals[i] = 0;
	//Skip leading '.' and command char
	uint8_t i = 2;
	uint8_t motor_num = 0;
	uint8_t mtr_tmp[4] = {10, 10, 10, 10};
	uint8_t mtr_tmp_pos = 0;
	while (motor_num < NUM_MOTORS)
	{	
		//look for the commas
		if (input[i] == ',' || input[i] == '\n')
		{
			if (mtr_tmp[3] < 10)		vals[motor_num] = mtr_tmp[0]*1000 + mtr_tmp[1]*100 + mtr_tmp[2]*10 + mtr_tmp[3];
			else if (mtr_tmp[2] < 10)	vals[motor_num] = mtr_tmp[0]*100 + mtr_tmp[1]*10 + mtr_tmp[2];
			else if (mtr_tmp[1] < 10)	vals[motor_num] = mtr_tmp[0]*10 + mtr_tmp[1];
			else						vals[motor_num] = mtr_tmp[0];
				
			motor_num++;
			for (uint8_t j = 0; j<4; j++) mtr_tmp[j] = 10;
			mtr_tmp_pos = 0;
			
		}
		else
		{
			mtr_tmp[mtr_tmp_pos] = input[i] - '0';
			mtr_tmp_pos++;
		}
		i++;
	}
}

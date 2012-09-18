/*
	Creative Machines Lab Aracna Firmware - Pin Macros
	Copyright (c) Creative Machines Lab, Cornell University, 2012
	Authored by Jeremy Blum and Eric Gold

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

#ifndef _MACROS_H_
#define _MACROS_H_

	//DEBUG LED - PB0 (ACTIVE HIGH)
	#define DEBUG_LED_NUM  			(1 << 0) 
	#define DEBUG_LED_ON()			PORTB |= (DEBUG_LED_NUM)
	#define DEBUG_LED_OFF()			PORTB &= ~(DEBUG_LED_NUM)
	#define DEBUG_LED_TOGGLE()		PORTB ^= (DEBUG_LED_NUM)
	#define DEBUG_LED_STATE()		(PINB & DEBUG_LED_NUM) ? 1 : 0
	
	//UART MACROS - Adapted from Wiring.h
	#define bitRead(value, bit) (((value) >> (bit)) & 0x01)
	#define bitSet(value, bit) ((value) |= (1UL << (bit)))
	#define bitClear(value, bit) ((value) &= ~(1UL << (bit)))
	#define bitWrite(value, bit, bitvalue) (bitvalue ? bitSet(value, bit) : bitClear(value, bit))
	#define bit(b) (1UL << (b))

#endif
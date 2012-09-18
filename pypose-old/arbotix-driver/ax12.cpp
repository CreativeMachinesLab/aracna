/*
  ax12.cpp - ArbotiX library for AX/RX control.
  Copyright (c) 2008-2010 Michael E. Ferguson.  All right reserved.

  This library is free software; you can redistribute it and/or
  modify it under the terms of the GNU Lesser General Public
  License as published by the Free Software Foundation; either
  version 2.1 of the License, or (at your option) any later version.

  This library is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public
  License along with this library; if not, write to the Free Software
  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include "wiring.h" // we need this for the serial port defines

#include "ax12.h"
#include <avr/interrupt.h>

/******************************************************************************
 * Hardware Serial Level, this uses the same stuff as Serial1, therefore 
 *  you should not use the Arduino Serial1 library.
 */

unsigned char ax_rx_buffer[AX12_BUFFER_SIZE];
unsigned char ax_tx_buffer[AX12_BUFFER_SIZE];
unsigned char ax_rx_int_buffer[AX12_BUFFER_SIZE];

// making these volatile keeps the compiler from optimizing loops of available()
volatile int ax_rx_Pointer;
volatile int ax_tx_Pointer;
volatile int ax_rx_int_Pointer;

#if defined(ARBOTIX_PLUS) || defined(SERVO_STIK)
  /* Write to RX bus */
  void setRX_WR(){
    #ifdef SERVO_STIK
      PORTC |= 0x40;
    #else
      PORTG |= 0x08;
    #endif
      bitClear(UCSR1B, RXEN1);    
      ax_tx_Pointer = 0;
  }
  /* Write to AX bus */
  void setAX_WR(){
    #ifdef SERVO_STIK
      PORTC |= 0x80;
    #else
      PORTG |= 0x10;
    #endif
      bitClear(UCSR1B, RXEN1);    
      ax_tx_Pointer = 0;
  }
  /* Read from RX bus */
  void setRX_RD(){
      int i;
      // Need to wait for last byte to be sent before turning the bus around.
      // Check the Transmit complete flag
      while (bit_is_clear(UCSR1A, UDRE1));
      for(i=0; i<UBRR1L*20; i++)    
          asm("nop");
    #ifdef SERVO_STIK
      PORTC = 0x80;
    #else
      PORTG = ( (PORTG&0xE7) | 0x10 );
    #endif
      asm("nop");
      asm("nop");
      asm("nop");
      //bitClear(UCSR1B, TXEN1);
      bitSet(UCSR1B, RXEN1);
      ax_rx_int_Pointer = 0;
      ax_rx_Pointer = 0;
  }
  /* Read from AX bus */
  void setAX_RD(){
      int i;
      // Need to wait for last byte to be sent before turning the bus around.
      // Check the Transmit complete flag
      while (bit_is_clear(UCSR1A, UDRE1));
      for(i=0; i<UBRR1L*20; i++)    
          asm("nop");
    #ifdef SERVO_STIK
      PORTC = 0x40;
    #else
      PORTG = ( (PORTG&0xE7) | 0x08 );
    #endif
      asm("nop");
      asm("nop");
      asm("nop");
      //bitClear(UCSR1B, TXEN1);
      bitSet(UCSR1B, RXEN1);
      ax_rx_int_Pointer = 0;
      ax_rx_Pointer = 0;
  }
  unsigned char dynamixel_bus_config[AX12_MAX_SERVOS];
#endif

/** helper functions to switch direction of comms */
void setTX(int id){
  #if defined(ARBOTIX_PLUS) || defined(SERVO_STIK)
    if(dynamixel_bus_config[id-1] > 0)
        setRX_WR();
    else
        setAX_WR();
  #else
    // emulate half-duplex on ArbotiX, ArbotiX w/ RX Bridge
    #ifdef ARBOTIX_WITH_RX
      PORTD |= 0x10;
    #endif
    bitClear(UCSR1B, RXEN1);    
    bitSet(UCSR1B, TXEN1);
    bitClear(UCSR1B, RXCIE1);
    ax_tx_Pointer = 0;
  #endif
}
void setRX(int id){ 
  #if defined(ARBOTIX_PLUS) || defined(SERVO_STIK)
    if(dynamixel_bus_config[id-1] > 0)
        setRX_RD();
    else
        setAX_RD();
  #else
    // emulate half-duplex on ArbotiX, ArbotiX w/ RX Bridge
    #ifdef ARBOTIX_WITH_RX
      int i;
      // Need to wait for last byte to be sent before turning the bus around.
      // Check the Transmit complete flag
      while (bit_is_clear(UCSR1A, UDRE1));
      for(i=0; i<25; i++)    
          asm("nop");
      PORTD &= 0xEF;
    #endif 
    bitClear(UCSR1B, TXEN1);
    bitSet(UCSR1B, RXEN1);
    bitSet(UCSR1B, RXCIE1);
    ax_rx_int_Pointer = 0;
    ax_rx_Pointer = 0;
  #endif  
}
// for sync write
void setTXall(){
  #if defined(ARBOTIX_PLUS) || defined(SERVO_STIK)
    setRX_WR();
    setAX_WR();
  #else
    #ifdef ARBOTIX_WITH_RX
      PORTD |= 0x10;
    #endif
    bitClear(UCSR1B, RXEN1);    
    bitSet(UCSR1B, TXEN1);
    bitClear(UCSR1B, RXCIE1);
    ax_tx_Pointer = 0;
  #endif
}

/** Sends a character out the serial port. */
void ax12write(unsigned char data){
    while (bit_is_clear(UCSR1A, UDRE1));
    UDR1 = data;
}
/** Sends a character out the serial port, and puts it in the tx_buffer */
void ax12writeB(unsigned char data){
    ax_tx_buffer[(ax_tx_Pointer++)] = data; 
    while (bit_is_clear(UCSR1A, UDRE1));
    UDR1 = data;
}
/** We have a one-way recieve buffer, which is reset after each packet is receieved.
    A wrap-around buffer does not appear to be fast enough to catch all bytes at 1Mbps. */
ISR(USART1_RX_vect){
    ax_rx_int_buffer[(ax_rx_int_Pointer++)] = UDR1;
}

/** read back the error code for our latest packet read */
int ax12Error;
/** > 0 = success */
int ax12ReadPacket(int length){
    unsigned long ulCounter;
    unsigned char offset, blength, checksum, timeout;
    unsigned char volatile bcount; 

    offset = 0;
    timeout = 0;
    bcount = 0;
    while(bcount < length){
        ulCounter = 0;
        while((bcount + offset) == ax_rx_int_Pointer){
            if(ulCounter++ > 1000L){ // was 3000
                timeout = 1;
                break;
            }
        }
        if(timeout) break;
        ax_rx_buffer[bcount] = ax_rx_int_buffer[bcount + offset];
        if((bcount == 0) && (ax_rx_buffer[0] != 0xff))
            offset++;
        else
            bcount++;
    }

    blength = bcount;
    checksum = 0;
    for(offset=2;offset<bcount;offset++)
        checksum += ax_rx_buffer[offset];
    if((checksum%256) != 255){
        return 0;
    }else{
        return 1;
    }
}

/** initializes serial1 transmit at baud, 8-N-1 */
void ax12Init(long baud){
    //UBRR1H = ((F_CPU / 16 + baud / 2) / baud - 1) >> 8;
    //UBRR1L = ((F_CPU / 16 + baud / 2) / baud - 1);
    UBRR1H = (F_CPU / (8 * baud) - 1 ) >> 8;
    UBRR1L = (F_CPU / (8 * baud) - 1 );
    bitSet(UCSR1A, U2X1);
    ax_rx_int_Pointer = 0;
    ax_rx_Pointer = 0;
    ax_tx_Pointer = 0;
#if defined(ARBOTIX_PLUS) || defined(SERVO_STIK)
  #if defined(ARBOTIX_PLUS)
    DDRG |= 0x18;
    PORTG |= 0x18;  // enable all out
  #else
    DDRC |= 0xC0;
    PORTC |= 0xC0;  // enable all out
  #endif
    bitSet(UCSR1B, TXEN1);
    bitSet(UCSR1B, RXEN1);
    bitSet(UCSR1B, RXCIE1);
#else
  #ifdef ARBOTIX_WITH_RX
    DDRD |= 0x10;   // Servo B = output
    PORTD &= 0xEF;  // Servo B low
  #endif
    // enable rx
    setRX(0);    
#endif
}

/******************************************************************************
 * Packet Level
 */

/** Read register value(s) */
int ax12GetRegister(int id, int regstart, int length){  
    setTX(id);
    // 0xFF 0xFF ID LENGTH INSTRUCTION PARAM... CHECKSUM    
    int checksum = ~((id + 6 + regstart + length)%256);
    ax12writeB(0xFF);
    ax12writeB(0xFF);
    ax12writeB(id);
    ax12writeB(4);    // length
    ax12writeB(AX_READ_DATA);
    ax12writeB(regstart);
    ax12writeB(length);
    ax12writeB(checksum);  
    setRX(id);    
    if(ax12ReadPacket(length + 6) > 0){
        ax12Error = ax_rx_buffer[4];
        if(length == 1)
            return ax_rx_buffer[5];
        else
            return ax_rx_buffer[5] + (ax_rx_buffer[6]<<8);
    }else{
        return -1;
    }
}

/* Set the value of a single-byte register. */
void ax12SetRegister(int id, int regstart, int data){
    setTX(id);    
    int checksum = ~((id + 4 + AX_WRITE_DATA + regstart + (data&0xff)) % 256);
    ax12writeB(0xFF);
    ax12writeB(0xFF);
    ax12writeB(id);
    ax12writeB(4);    // length
    ax12writeB(AX_WRITE_DATA);
    ax12writeB(regstart);
    ax12writeB(data&0xff);
    // checksum = 
    ax12writeB(checksum);
    setRX(id);
    //ax12ReadPacket();
}
/* Set the value of a double-byte register. */
void ax12SetRegister2(int id, int regstart, int data){
    setTX(id);    
    int checksum = ~((id + 5 + AX_WRITE_DATA + regstart + (data&0xFF) + ((data&0xFF00)>>8)) % 256);
    ax12writeB(0xFF);
    ax12writeB(0xFF);
    ax12writeB(id);
    ax12writeB(5);    // length
    ax12writeB(AX_WRITE_DATA);
    ax12writeB(regstart);
    ax12writeB(data&0xff);
    ax12writeB((data&0xff00)>>8);
    // checksum = 
    ax12writeB(checksum);
    setRX(id);
    //ax12ReadPacket();
}

// general write?
// general sync write?


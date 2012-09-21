/*
  Adapted for Creative Machines Lab Aracna Firmware
  uart.h - UART0 Control Library
  Changes Copyright (c) Creative Machines Lab, Cornell University, 2012 - http://www.creativemachines.org
  Changes Authored by Jeremy Blum - http://www.jeremyblum.com
  
  Original Copyright (c) 2008-2012 Ronald Willem Besinga.  All right reserved.
  http://www.ermicro.com/blog/?p=325

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

void uart_putchar(char c, FILE *stream);
char uart_getchar(FILE *stream);

void uart_init(void);

FILE uart_output = FDEV_SETUP_STREAM(uart_putchar, NULL, _FDEV_SETUP_WRITE);
FILE uart_input = FDEV_SETUP_STREAM(NULL, uart_getchar, _FDEV_SETUP_READ);
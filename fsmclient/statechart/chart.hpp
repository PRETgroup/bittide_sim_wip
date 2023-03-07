/*
 * Automatically generated C code by
 * KIELER SCCharts - The Key to Efficient Modeling
 *
 * http://rtsys.informatik.uni-kiel.de/kieler
 */

#ifndef _ABRO_H_
#define _ABRO_H_
#include <iostream>
#include <vector>
// The chosen scheduling regime (IUR) uses four states to maintain the statuses of threads."),
typedef enum {
  TERMINATED,
  RUNNING,
  READY,
  PAUSING
} ThreadStatus;

// Interface
typedef struct {
  char A; // Input
  char B; // Input
  char R; // Input
  char O; // Output
} Iface;

char* inputsFromStr(Iface* iface, std::string s);
std::vector<std::string> getPresentOutputs(Iface* iface); //TODO: Implement
 
// This enum contains all states of the  region
typedef enum {
    WB, DB1
} ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3States;

// The thread data of 
typedef struct {
  ThreadStatus threadStatus; 
  ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3States activeState; 
  char delayedEnabled; 
  Iface* iface; 
} ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3Context;
 
// This enum contains all states of the  region
typedef enum {
    WA, DA1
} ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2States;

// The thread data of 
typedef struct {
  ThreadStatus threadStatus; 
  ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2States activeState; 
  char delayedEnabled; 
  Iface* iface; 
} ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2Context;
 
// This enum contains all states of the  region
typedef enum {
    WAITAB, WAITABRUNNING, DONE, _AABORTED, _AC1, __EA_INIT1
} ABRO_regionR0_stateABO_regionR1States;

// The thread data of 
typedef struct {
  ThreadStatus threadStatus; 
  ABRO_regionR0_stateABO_regionR1States activeState; 
  char delayedEnabled; 
  Iface* iface; 
  ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2Context ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2;
  ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3Context ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3;
} ABRO_regionR0_stateABO_regionR1Context;
 
// This enum contains all states of the  region
typedef enum {
    ABO, ABORUNNING, __EA_INIT
} ABRO_regionR0States;

// The thread data of 
typedef struct {
  ThreadStatus threadStatus; 
  ABRO_regionR0States activeState; 
  char delayedEnabled; 
  Iface* iface; 
  ABRO_regionR0_stateABO_regionR1Context ABRO_regionR0_stateABO_regionR1;
} ABRO_regionR0Context;

// Root level data of the program
typedef struct {
  Iface iface;
  ThreadStatus threadStatus;
  char delayedEnabled;
  
  ABRO_regionR0Context ABRO_regionR0;
} TickData;



void reset(TickData *context);
void tick(TickData *context);

#endif
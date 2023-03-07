/*
 * Automatically generated C code by
 * KIELER SCCharts - The Key to Efficient Modeling
 *
 * http://rtsys.informatik.uni-kiel.de/kieler
 */
#include <stdio.h>
#include "chart.hpp"

char* fromChar(Iface* iface, char s) {
  if (s == 'A') return &iface->A;
  else if (s == 'B') return &iface->B;
  else if (s == 'R') return &iface->R;
  else if (s == 'O') return &iface->O;
  else return 0;
}
static inline void ABRO_regionR0_state__EA_Init(ABRO_regionR0Context *context) {
  context->iface->O = 0;
  context->delayedEnabled = 0;
  context->activeState = ABO;
}

static inline void ABRO_regionR0_stateABO_regionR1_state__EA_Init1(ABRO_regionR0_stateABO_regionR1Context *context) {
  context->iface->O = 0;
  context->delayedEnabled = 0;
  context->activeState = WAITAB;
}

static inline void ABRO_regionR0_stateABO_regionR1_state_AC1(ABRO_regionR0_stateABO_regionR1Context *context) {
  if (context->iface->R) {
    context->delayedEnabled = 0;
    context->activeState = _AABORTED;
  } else {
    context->iface->O = 1;
    context->delayedEnabled = 0;
    context->activeState = DONE;
  }
}

static inline void ABRO_regionR0_stateABO_regionR1_state_Aaborted(ABRO_regionR0_stateABO_regionR1Context *context) {
  context->threadStatus = TERMINATED;
}

static inline void ABRO_regionR0_stateABO_regionR1_statedone(ABRO_regionR0_stateABO_regionR1Context *context) {
  if (context->delayedEnabled && (context->iface->R)) {
    context->delayedEnabled = 0;
    context->activeState = _AABORTED;
  } else {
    context->threadStatus = READY;
  }
}

static inline void ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3_statedB1(ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3Context *context) {
  context->threadStatus = TERMINATED;
}

static inline void ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3_statewB(ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3Context *context) {
  if (context->delayedEnabled && (context->iface->R)) {
    context->delayedEnabled = 0;
    context->activeState = DB1;
  } else if (context->delayedEnabled && (context->iface->B)) {
    context->delayedEnabled = 0;
    context->activeState = DB1;
  } else {
    context->threadStatus = READY;
  }
}

static void ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3(ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3Context *context) {
  while (context->threadStatus == RUNNING) {
    switch (context->activeState) {
      case WB:
        ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3_statewB(context);
                break;
      
      case DB1:
        ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3_statedB1(context);
                break;
      
    }
  }
}

static inline void ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2_statedA1(ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2Context *context) {
  context->threadStatus = TERMINATED;
}

static inline void ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2_statewA(ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2Context *context) {
  if (context->delayedEnabled && (context->iface->R)) {
    context->delayedEnabled = 0;
    context->activeState = DA1;
  } else if (context->delayedEnabled && (context->iface->A)) {
    context->delayedEnabled = 0;
    context->activeState = DA1;
  } else {
    context->threadStatus = READY;
  }
}

static void ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2(ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2Context *context) {
  while (context->threadStatus == RUNNING) {
    switch (context->activeState) {
      case WA:
        ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2_statewA(context);
                break;
      
      case DA1:
        ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2_statedA1(context);
                break;
      
    }
  }
}

static inline void ABRO_regionR0_stateABO_regionR1_stateWaitAB(ABRO_regionR0_stateABO_regionR1Context *context) {

  context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2.activeState = WA;
  context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2.delayedEnabled = 0;
  context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2.threadStatus = READY;

  context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3.activeState = WB;
  context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3.delayedEnabled = 0;
  context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3.threadStatus = READY;
  context->activeState = WAITABRUNNING;
}


static inline void ABRO_regionR0_stateABO_regionR1_stateWaitAB_running(ABRO_regionR0_stateABO_regionR1Context *context) {

  if (context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2.threadStatus != TERMINATED) {
    context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2.threadStatus = RUNNING;
  }
  

  if (context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3.threadStatus != TERMINATED) {
    context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3.threadStatus = RUNNING;
  }
  

  ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2(&context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2);

  ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3(&context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3);

  if (context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2.threadStatus == TERMINATED && 
      context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3.threadStatus == TERMINATED) {
    context->delayedEnabled = 0;
    context->activeState = _AC1;
  } else {
  
      context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2.delayedEnabled = 1;
      context->ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3.delayedEnabled = 1;
    context->threadStatus = READY;
  }

}

static void ABRO_regionR0_stateABO_regionR1(ABRO_regionR0_stateABO_regionR1Context *context) {
  while (context->threadStatus == RUNNING) {
    switch (context->activeState) {
      case WAITAB:
        ABRO_regionR0_stateABO_regionR1_stateWaitAB(context);
        // Superstate: intended fall-through 
      case WAITABRUNNING:
        ABRO_regionR0_stateABO_regionR1_stateWaitAB_running(context);
        break;
      
      case DONE:
        ABRO_regionR0_stateABO_regionR1_statedone(context);
                break;
      
      case _AABORTED:
        ABRO_regionR0_stateABO_regionR1_state_Aaborted(context);
                break;
      
      case _AC1:
        ABRO_regionR0_stateABO_regionR1_state_AC1(context);
                break;
      
      case __EA_INIT1:
        ABRO_regionR0_stateABO_regionR1_state__EA_Init1(context);
                break;
      
    }
  }
}

static inline void ABRO_regionR0_stateABO(ABRO_regionR0Context *context) {

  context->ABRO_regionR0_stateABO_regionR1.activeState = __EA_INIT1;
  context->ABRO_regionR0_stateABO_regionR1.delayedEnabled = 0;
  context->ABRO_regionR0_stateABO_regionR1.threadStatus = READY;
  context->activeState = ABORUNNING;
}


static inline void ABRO_regionR0_stateABO_running(ABRO_regionR0Context *context) {

  if (context->ABRO_regionR0_stateABO_regionR1.threadStatus != TERMINATED) {
    context->ABRO_regionR0_stateABO_regionR1.threadStatus = RUNNING;
  }
  

  ABRO_regionR0_stateABO_regionR1(&context->ABRO_regionR0_stateABO_regionR1);

  if (context->ABRO_regionR0_stateABO_regionR1.threadStatus == TERMINATED) {
    context->delayedEnabled = 0;
    context->activeState = ABO;
  } else {
  
      context->ABRO_regionR0_stateABO_regionR1.delayedEnabled = 1;
    context->threadStatus = READY;
  }

}

static void ABRO_regionR0(ABRO_regionR0Context *context) {
  while (context->threadStatus == RUNNING) {
    switch (context->activeState) {
      case ABO:
        ABRO_regionR0_stateABO(context);
        // Superstate: intended fall-through 
      case ABORUNNING:
        ABRO_regionR0_stateABO_running(context);
        break;
      
      case __EA_INIT:
        ABRO_regionR0_state__EA_Init(context);
                break;
      
    }
  }
}

static inline void ABRO(TickData *context) {

  if (context->ABRO_regionR0.threadStatus != TERMINATED) {
    context->ABRO_regionR0.threadStatus = RUNNING;
  }
  

  ABRO_regionR0(&context->ABRO_regionR0);


  context->ABRO_regionR0.delayedEnabled = 1;
  context->threadStatus = READY;

}

void reset(TickData *context) {
  context->ABRO_regionR0.iface = &(context->iface);
  context->ABRO_regionR0.ABRO_regionR0_stateABO_regionR1.iface = &(context->iface);
  context->ABRO_regionR0.ABRO_regionR0_stateABO_regionR1.ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR2.iface = &(context->iface);
  context->ABRO_regionR0.ABRO_regionR0_stateABO_regionR1.ABRO_regionR0_stateABO_regionR1_stateWaitAB_regionR3.iface = &(context->iface);
  context->ABRO_regionR0.activeState = __EA_INIT;
  context->ABRO_regionR0.threadStatus = READY;
  
  context->threadStatus = READY;
  context->delayedEnabled = 0;
}

void tick(TickData *context) {
  if (context->threadStatus == TERMINATED) return;
  
  ABRO(context);
  context->delayedEnabled = 1;
}


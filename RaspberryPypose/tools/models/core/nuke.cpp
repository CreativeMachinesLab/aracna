#include <ax12.h>
#include <BioloidController.h>
#include <WProgram.h>
#include <math.h>
#include "nuke.h"

/* min and max positions for each servo */                                          
@SERVO_MINS
@SERVO_MAXS

/* IK Engine */
BioloidController bioloid = BioloidController(1000000);
ik_req_t endpoints[LEG_COUNT];
float bodyRotX = 0;             // body roll (rad)
float bodyRotY = 0;             // body pitch (rad)
float bodyRotZ = 0;             // body rotation (rad)
int bodyPosX = 0;               // body offset (mm)
int bodyPosY = 0;               // body offset (mm)
int Xspeed;                     // forward speed (mm/s)
int Yspeed;                     // sideward speed (mm/s)
float Rspeed;                   // rotation speed (rad/s)

/* Gait Engine */
int gaitLegNo[LEG_COUNT];       // order to step through legs
ik_req_t gaits[LEG_COUNT];      // gait engine output
int pushSteps;                  // how much of the cycle we are on the ground
int stepsInCycle;               // how many steps in this cycle
int step;                       // current step 
int tranTime;
int liftHeight;
float cycleTime;                // cycle time in seconds (adjustment from speed to step-size)

/* Setup the starting positions of the legs. */
void setupIK(){
  endpoints[RIGHT_FRONT].x = @X_STANCE;
  endpoints[RIGHT_FRONT].y = @Y_STANCE;
  endpoints[RIGHT_FRONT].z = @Z_STANCE;
                    
  endpoints[RIGHT_REAR].x = -@X_STANCE;
  endpoints[RIGHT_REAR].y = @Y_STANCE;
  endpoints[RIGHT_REAR].z = @Z_STANCE;
@IF legs 6

  endpoints[RIGHT_MIDDLE].x = 0;
  endpoints[RIGHT_MIDDLE].y = @Y_STANCE;
  endpoints[RIGHT_MIDDLE].z = @Z_STANCE;

  endpoints[LEFT_MIDDLE].x = 0;
  endpoints[LEFT_MIDDLE].y = -@Y_STANCE;
  endpoints[LEFT_MIDDLE].z = @Z_STANCE;  
@END_IF

  endpoints[LEFT_FRONT].x = @X_STANCE;
  endpoints[LEFT_FRONT].y = -@Y_STANCE;
  endpoints[LEFT_FRONT].z = @Z_STANCE;
    
  endpoints[LEFT_REAR].x = -@X_STANCE;
  endpoints[LEFT_REAR].y = -@Y_STANCE;
  endpoints[LEFT_REAR].z = @Z_STANCE;

  liftHeight = @LIFT_HEIGHT;
  stepsInCycle = 1;
  step = 0;
}

#include "gaits.h"

/* Convert radians to servo position offset. */
int radToServo(float rads){ 
  float val = (rads*100)/51 * @RAD_TO_SERVO_RESOLUTION;
  return (int) val; 
}

/* Body IK solver: compute where legs should be. */
ik_req_t bodyIK(int X, int Y, int Z, int Xdisp, int Ydisp, float Zrot){
    ik_req_t ans;
    
    float cosB = cos(bodyRotX);
    float sinB = sin(bodyRotX);
    float cosG = cos(bodyRotY);
    float sinG = sin(bodyRotY);
    float cosA = cos(bodyRotZ+Zrot);
    float sinA = sin(bodyRotZ+Zrot);
    
    int totalX = X + Xdisp + bodyPosX; 
    int totalY = Y + Ydisp + bodyPosY; 
    
    ans.x = totalX - int(totalX*cosG*cosA + totalY*sinB*sinG*cosA + Z*cosB*sinG*cosA - totalY*cosB*sinA + Z*sinB*sinA) + bodyPosX;
    ans.y = totalY - int(totalX*cosG*sinA + totalY*sinB*sinG*sinA + Z*cosB*sinG*sinA + totalY*cosB*cosA - Z*sinB*cosA) + bodyPosY;
    ans.z = Z - int(-totalX*sinG + totalY*sinB*cosG + Z*cosB*cosG);
    
    return ans;
}

@LEG_IK

void doIK(){
@DO_IK
}


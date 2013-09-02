@HEADER
#ifndef NUKE
#define NUKE

@IF legs 4
#define LEG_COUNT   4

/* Body 
 * We assume 4 legs are on the corners of a box defined by X_COXA x Y_COXA 
 */
#define X_COXA      @VAL_XCOXA  // MM between front and back legs /2
#define Y_COXA      @VAL_YCOXA  // MM between front/back legs /2
@ELSE
#define LEG_COUNT   6

/* Body 
 * We assume 4 legs are on the corners of a box defined by X_COXA x Y_COXA 
 * Middle legs for a hexapod can be different Y, but should be halfway in X 
 */
#define X_COXA      @VAL_XCOXA  // MM between front and back legs /2
#define Y_COXA      @VAL_YCOXA  // MM between front/back legs /2
#define M_COXA      @VAL_MCOXA  // MM between two middle legs /2
@END_IF

/* Legs */
#define L_COXA      @VAL_LCOXA  // MM distance from coxa servo to femur servo 
#define L_FEMUR     @VAL_LFEMUR // MM distance from femur servo to tibia servo 
#define L_TIBIA     @VAL_LTIBIA // MM distance from tibia servo to foot 

/* Servo IDs */
@SERVO_INDEXES
/* A leg position request (output of body calcs, input to simple 3dof solver). */
typedef struct{
    int x;
    int y;
    int z;
    float r;
} ik_req_t;

/* Servo ouptut values (output of 3dof leg solver). */
typedef struct{
    int coxa;
    int femur;
    int tibia;
} ik_sol_t;

/* Actual positions, and indices of array. */
extern ik_req_t endpoints[LEG_COUNT];
#define RIGHT_FRONT    0
#define RIGHT_REAR     1
#define LEFT_FRONT     2
#define LEFT_REAR      3
@IF legs 6
#define RIGHT_MIDDLE   4
#define LEFT_MIDDLE    5
@END_IF

extern BioloidController bioloid;

/* Parameters for manipulating body position */
extern float bodyRotX;    // body roll
extern float bodyRotY;    // body pitch
extern float bodyRotZ;    // body rotation
extern int bodyPosX;
extern int bodyPosY;

/* Parameters for gait manipulation */
extern int Xspeed;
extern int Yspeed;
extern float Rspeed;
extern int tranTime;
extern float cycleTime;
extern int stepsInCycle;
extern int liftHeight;
extern int step;

/* Gait Engine */
extern int gaitLegNo[];   // order to move legs in
extern ik_req_t gaits[];  // gait position

/* convert radians to a dynamixel servo offset */
int radToServo(float rads);
/* select a gait pattern to use */
void gaitSelect(int GaitType);

#include "gaits.h"

/* find the translation of the coxa point (x,y) in 3-space, given our rotations */
ik_req_t bodyIK(int X, int Y, int Z, int Xdisp, int Ydisp, float Zrot);
/* given our leg offset (x,y,z) from the coxa point, calculate servo values */
ik_sol_t legIK(int X, int Y, int Z);
/* ties all of the above together */
void doIK();
/* setup the starting positions of the legs. */
void setupIK();

#endif

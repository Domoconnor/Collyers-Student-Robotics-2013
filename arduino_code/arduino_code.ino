#include <AFMotor.h>

char opCode = 0;
char operand = 0;
boolean newInstruction = false;
int serialInputCounter = 0;

AF_DCMotor heliMotor( 1, MOTOR12_8KHZ );
AF_DCMotor grabberMotor( 2, MOTOR12_8KHZ );

void setHeliSpeed( int speed )
{
  int scaledSpeed = ( speed * 255 ) / 100;
  if( scaledSpeed < 0 )
  {
    heliMotor.setSpeed( -scaledSpeed );
    heliMotor.run( BACKWARD );
  }
  else if( scaledSpeed > 0 )
  {
    heliMotor.setSpeed( scaledSpeed );
    heliMotor.run( FORWARD );
  }
  else
  {
    heliMotor.setSpeed( 0 );
    heliMotor.run( RELEASE );
  }
}

void setGrabberSpeed( int speed )
{
  if( speed < 0 )
  {
    grabberMotor.setSpeed( -speed );
    grabberMotor.run( BACKWARD );
  }
  else if( speed > 0 )
  {
    grabberMotor.setSpeed( speed );
    grabberMotor.run( FORWARD );
  }
  else
  {
    grabberMotor.setSpeed( 0 );
    grabberMotor.run( RELEASE );
  }
}

void setup()
{
  Serial.begin( 9600 );
}

void loop()
{
  if( newInstruction == true )
  {
    switch( (int)opCode )
    {
    case 33:
      setHeliSpeed( (int)operand - 100 );
      break;
    case 34:
      setGrabberSpeed( (int)operand - 100 );
      break;
    default:
      break;
    }
    newInstruction = false;
  } 
}

void serialEvent()
{
  while( Serial.available() )
  {
    // get the new byte:
    char inChar = (char)Serial.read();
    serialInputCounter++;
    if( serialInputCounter == 1 )
    {
      opCode = inChar;
    }
    else if( serialInputCounter == 2 )
    {
      operand = inChar;
      newInstruction = true;
      serialInputCounter = 0;
    }
  }
}

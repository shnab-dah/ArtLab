#define dirPin 2
#define pulsePin 3

const byte numChars = 32;
char receivedData[numChars];
char tempData[numChars];
int functionCalled = 0;
int int1Data = 0;
int int2Data = 100;
int int3Data = 0;
int int4Data = 0;
boolean newData = false; 


void setup() {
  Serial.begin(9600); // initiate serial connection
  Serial.println("<INITIALIZING>");
  pinMode(dirPin, OUTPUT);
  pinMode(pulsePin, OUTPUT);
  Serial.println("FOCUS STACKING v0.01");
  Serial.println("COMMANDS:");
  Serial.println("<0,$STEPS,$SPEED> - STEP FORWARD");
  Serial.println("<1,$STEPS,$SPEED> - STEP BACKWARD");
  Serial.println("<INITIALIZED>");
  Serial.println("----------------");
}

void loop()
{
  recvData();
  if (newData == true){
    strcpy(tempData, receivedData);
    parseData();
    callFunction();
    newData=false;
  }
}

void stepForward(unsigned int steps, int speed){
  Serial.print("<MOVING ");
  Serial.print(steps);
  Serial.print(" FORWARD WITH SPEED ");
  Serial.print(speed);
  Serial.println(">");
  for (int i=0; i<steps; i++){
    digitalWrite(dirPin, LOW);
    digitalWrite(pulsePin, HIGH);
    delayMicroseconds(speed);
    digitalWrite(pulsePin, LOW);
    delayMicroseconds(speed);
  }
  Serial.println("<MOVEMENT COMPLETE>");
}

void stepBack(unsigned int steps, int speed){
  Serial.print("<MOVING ");
  Serial.print(steps);
  Serial.print(" BACK WITH SPEED ");
  Serial.print(speed);
  Serial.println(">");  
  for (int i=0; i<steps; i++){
    digitalWrite(dirPin, HIGH);
    digitalWrite(pulsePin, HIGH);
    delayMicroseconds(speed);
    digitalWrite(pulsePin, LOW);
    delayMicroseconds(speed);
  }
  Serial.println("<MOVEMENT COMPLETE>");
}


//Serial data
//call function based on serial input
void callFunction(){
  // 0 = forwards. 
  if(functionCalled == 0){
    stepForward(int1Data, int2Data);}
  // 1 = step backwards
  else if(functionCalled == 1){
    stepBack(int1Data, int2Data);}
  // error
  else{
    Serial.print("<INCORRECT FUNCTION CALL: ");
    Serial.print(functionCalled);
    Serial.println(">");
  }
}



// receive serial data
// recieves and appends data send between startMarker and endMarker
void recvData(){
  static boolean receivingData = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;
  
  while (Serial.available() > 0 && newData == false){
    rc = Serial.read();
    
    if (receivingData == true){
      // append new character to receivedData
      if (rc != endMarker){
        receivedData[ndx] = rc;
        ndx++;
        // overflow buffer
        if (ndx >= numChars){
          ndx = numChars -1;
        }
      }
      // end receiving
      else {
        receivedData[ndx] = '\0';
        receivingData = false;
        ndx = 0;
        // flag new data
        newData = true;
      }
    }
    // starts recieving at "<"
    else if (rc == startMarker){
      receivingData = true;
    }
  }
}


// parse data input to INTs <FUNCTION, INT1, INT2, INT3, INT4>
void parseData(){
  char * strtokIndx;
  
  strtokIndx = strtok(tempData, ",");
  functionCalled = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int1Data = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int2Data = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int3Data = atoi(strtokIndx);
  
  strtokIndx = strtok(NULL, ",");
  int4Data = atoi(strtokIndx);
}
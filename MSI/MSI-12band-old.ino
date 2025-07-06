const int row1[3]{16,15,14};
const int col1[4]{4,5,6,7};
const int row2[3]{17,18,19};
const int col2[4]{8,9,10,11};

boolean completeCapture = false;

//variables for serial protocol
const byte numChars = 32;
char receivedData[numChars];
char tempData[numChars];
int functionCalled = 0;
int int1Data = 0;
int int2Data = 0;
int int3Data = 0;
int int4Data = 0;
boolean newData = false;

void setup() {
  Serial.begin(9600); // initiate serial connection
  Serial.println("<INITIALIZING>");
  // put your setup code here, to run once:
  for(int x = 0; x < 3; x++){
    pinMode(row1[x], OUTPUT);
    digitalWrite(row1[x], HIGH);
    pinMode(row2[x], OUTPUT);
    digitalWrite(row2[x], HIGH);
  }
  for(int x = 0; x < 4; x++){
    pinMode(col1[x], OUTPUT);
    pinMode(col2[x], OUTPUT);
  }
  Serial.println("<INITIALIZED>");
  lightsOn();
}

void loop() {
  recvData();
  if (newData == true){
    strcpy(tempData, receivedData);
    parseData();
    callFunction();
    newData=false;
  }
}

void lightsOn(){
  for(int x = 0; x < 4; x++){
    digitalWrite(col1[x], HIGH);
    digitalWrite(col2[x], HIGH);
  }
  for(int y = 0; y < 3; y++){
    digitalWrite(row1[y], LOW);
    digitalWrite(row2[y], LOW);
  }
}

void lightsOff(){
  for(int x = 0; x < 4; x++){
    digitalWrite(col1[x], LOW);
    digitalWrite(col2[x], LOW);
  }
  for(int y = 0; y < 3; y++){
    digitalWrite(row1[y], HIGH);
    digitalWrite(row2[y], HIGH);
  }
}

void capture(int delayTime) {
  lightsOff();
  for(int x = 0; x < 3; x++){
    digitalWrite(row1[x], LOW);
    digitalWrite(row2[x], LOW);
    for (int y = 0; y < 4; y++){
      digitalWrite(col1[y], HIGH);
      digitalWrite(col2[y], HIGH);
      delay(5);
      Serial.println("<SHUTTER>");
      delay(delayTime);
      digitalWrite(col1[y], LOW);
      digitalWrite(col2[y], LOW);
    }
    digitalWrite(row1[x], HIGH);
    digitalWrite(row2[x], HIGH);
  }
  Serial.println("<CAPTURE_COMPLETE>");
  
  lightsOn();
  for (int _ =  0; _ < 3; _++){
    delay(300);
    lightsOff();
    delay (300);
    lightsOn();
  }
}


//Serial data
//call function based on serial input
void callFunction(){
  // 0 = Capture. 
  if(functionCalled == 0){
    capture(int1Data);}
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

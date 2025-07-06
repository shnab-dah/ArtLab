/*
MSI control v1.0
    control of 16-band msi-handheld system
Sjors H. Nab, 19/06/2025

Serial protocol:
Baud rate: 9600

*/

int lights[14] = {2, 3, 4, 5, 8, 9, 10, 11, A0, A1, A2, A3, A4, A5};

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
  Serial.begin(9600);

  // Set all light pins as OUTPUT and turn them OFF (HIGH = off in this case)
  for (int i = 0; i < 14; i++) {
    pinMode(lights[i], OUTPUT);
    digitalWrite(lights[i], HIGH);
  }
}

void loop() {
  recvData();
  if (newData == true) {
    strcpy(tempData, receivedData);
    parseData();
    callFunction();
    newData = false;
  }
}

void flash(int light, int durationMs) {
  if (light < 0 || light >= 14) return;

  digitalWrite(lights[light], LOW);  // Turn ON
  delay(durationMs);
  digitalWrite(lights[light], HIGH); // Turn OFF
}

void turnLightOn(int light) {
  if (light < 0 || light >= 14) return;
  digitalWrite(lights[light], LOW);
}

void turnLightOff(int light) {
  if (light < 0 || light >= 14) return;
  digitalWrite(lights[light], HIGH);
}

void cycle(int durationMs) {
  for (int i = 0; i < 14; i++) {
    flash(i, durationMs);
  }
}

void callFunction() {
  switch (functionCalled) {
    case 0:  // flash(light, duration)
      flash(int1Data, int2Data);
      break;

    case 1:  // cycle(duration)
      cycle(int1Data);
      break;

    case 2:  // turn light ON
      turnLightOn(int1Data);
      break;

    case 3:  // turn light OFF
      turnLightOff(int1Data);
      break;

    default:
      Serial.print("<INVALID FUNCTION: ");
      Serial.print(functionCalled);
      Serial.println(">");
      break;
  }
}

void recvData() {
  static boolean receiving = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (receiving) {
      if (rc != endMarker) {
        receivedData[ndx++] = rc;
        if (ndx >= numChars) ndx = numChars - 1;
      } else {
        receivedData[ndx] = '\0';  // null-terminate
        receiving = false;
        ndx = 0;
        newData = true;
      }
    } else if (rc == startMarker) {
      receiving = true;
    }
  }
}

void parseData() {
  char* strtokIndx;

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

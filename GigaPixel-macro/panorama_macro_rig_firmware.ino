// Define the stepper motor pins connected to the CNC shield
#define enPin 8     // Enable pin

#define dirPinX 5    // Direction pin for X-axis
#define stepPinX 2   // Step pin for X-axis
#define limitSwitchPinX 9 // Endpoint limit switch X-axis (active LOW when triggered)

#define dirPinY 6 // Direction pin for Y-axis
#define stepPinY 3 // Step pin for Y-axis
#define limitSwitchPinY 10 // Endpoint limit switch Y-axis

#define speed 75

bool directionX = HIGH;  // Initial direction of the motor
bool limitSwitchStateX = HIGH; // The current state of the limit switch

bool directionY = HIGH; // Initial direction of the Y-motor
bool limitSwitchStateY = HIGH; // Current state of the Y limit switch

uint32_t positionX;
uint32_t positionY;
uint32_t maxX;
uint32_t maxY;

void setup() {
  Serial.begin(115200);
  
  pinMode(dirPinX, OUTPUT); 
  pinMode(stepPinX, OUTPUT);
  pinMode(dirPinY, OUTPUT);
  pinMode(stepPinY, OUTPUT);
  pinMode(enPin, OUTPUT);
  pinMode(limitSwitchPinX, INPUT_PULLUP); 
  pinMode(limitSwitchPinY, INPUT_PULLUP);

  digitalWrite(enPin, LOW);
  digitalWrite(dirPinX, directionX);
  digitalWrite(dirPinY, directionY);

  Calibrate();
  delay(250);
  Center();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "CENTER") {
      Center();
    } else if (command.startsWith("MOVE")) {
      int spaceIndex = command.indexOf(' ');
      int commaIndex = command.indexOf(',');
      if (spaceIndex != -1 && commaIndex != -1) {
        uint32_t X = command.substring(spaceIndex + 1, commaIndex).toInt();
        uint32_t Y = command.substring(commaIndex + 1).toInt();
        moveTo(X, Y);
      }
    }
  }
}

void moveTo(uint32_t X, uint32_t Y) {
  X = constrain(X, 0, maxX);
  Y = constrain(Y, 0, maxY);

  if (X > positionX) {
    digitalWrite(dirPinX, LOW);
  } else {
    digitalWrite(dirPinX, HIGH);
  }

  while (positionX != X) {
    stepX();
    positionX += (X > positionX) ? 1 : -1;
  }

  delay(100);

  if (Y > positionY) {
    digitalWrite(dirPinY, LOW);
  } else {
    digitalWrite(dirPinY, HIGH);
  }
  
  while (positionY != Y) {
    stepY();
    positionY += (Y > positionY) ? 1 : -1;
  }

  delay(100);
  
  sendPosition();
}

void stepX() {
  digitalWrite(stepPinX, HIGH);
  delayMicroseconds(speed);
  digitalWrite(stepPinX, LOW);
  delayMicroseconds(speed);
}

void stepY() {
  digitalWrite(stepPinY, HIGH);
  delayMicroseconds(speed);
  digitalWrite(stepPinY, LOW);
  delayMicroseconds(speed);
}

void Center() {
  uint32_t targetX = maxX / 2;
  uint32_t targetY = maxY / 2;
  moveTo(targetX, targetY);
}

void Calibrate() {
  limitSwitchStateX = digitalRead(limitSwitchPinX);
  while (limitSwitchStateX == HIGH) {
    stepX();
    limitSwitchStateX = digitalRead(limitSwitchPinX);
  }

  delay(250);


  limitSwitchStateY = digitalRead(limitSwitchPinY);
  while (limitSwitchStateY == HIGH) {
    stepY();
    limitSwitchStateY = digitalRead(limitSwitchPinY);
  }

  positionX = 0;
  positionY = 0;

  directionX = !directionX;
  directionY = !directionY;
  digitalWrite(dirPinX, directionX);
  digitalWrite(dirPinY, directionY); 

  for (int n = 0; n < 2000; n++){
    stepX();
    positionX++;
  }

  for (int n = 0; n < 2000; n++){
    stepY();
    positionY++;
  }

  limitSwitchStateX = digitalRead(limitSwitchPinX);
  while (limitSwitchStateX == HIGH) {
    stepX();
    positionX += 1;
    limitSwitchStateX = digitalRead(limitSwitchPinX);
  }

  delay(100);


  limitSwitchStateY = digitalRead(limitSwitchPinY);
  while (limitSwitchStateY == HIGH) {
    stepY();
    positionY += 1;
    limitSwitchStateY = digitalRead(limitSwitchPinY);
  }

  maxX = positionX;
  maxY = positionY;

  Serial.print("CALIBRATED ");
  Serial.print(maxX);
  Serial.print(" ");
  Serial.println(maxY);
}

void sendPosition(){
  Serial.print("POSITION ");
  Serial.print(positionX);
  Serial.print(" ");
  Serial.println(positionY);
}

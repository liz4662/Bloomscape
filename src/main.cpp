#include <WebServer.h>

int threshold = 40;
const unsigned long cooldown = 250;
const unsigned long tapWindow = 500;

// flower flags
volatile bool touchFrangipani = false;
volatile bool touchDaisy = false;
volatile bool touchRose = false;
volatile bool touchTulip = false;
volatile bool touchForgetMeNot = false;

// control flags
volatile bool touchMode = false;
volatile bool touchReset = false;

// flower cooldown timers
unsigned long lastFrangipaniTime = 0;
unsigned long lastDaisyTime = 0;
unsigned long lastRoseTime = 0;
unsigned long lastTulipTime = 0;
unsigned long lastForgetMeNotTime = 0;
unsigned long lastResetTime = 0;

// mode tap logic
unsigned long lastModeTouchTime = 0;
unsigned long lastTapTime = 0;
int tapCount = 0;

// interrupts
void gotFrangipani() { touchFrangipani = true; }
void gotDaisy() { touchDaisy = true; }
void gotRose() { touchRose = true; }
void gotTulip() { touchTulip = true; }
void gotForgetMeNot() { touchForgetMeNot = true; }

void gotMode() { touchMode = true; }
void gotReset() { touchReset = true; }

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Garden controller ready");

  // flowers
  touchAttachInterrupt(T2, gotFrangipani, threshold);    // GPIO 2
  touchAttachInterrupt(T9, gotDaisy, threshold);         // GPIO 32
  touchAttachInterrupt(T4, gotRose, threshold);          // GPIO 13
  touchAttachInterrupt(T3, gotTulip, threshold);         // GPIO 15
  touchAttachInterrupt(T5, gotForgetMeNot, threshold);   // GPIO 12

  // controls
  touchAttachInterrupt(T7, gotMode, threshold);          // GPIO 27
  touchAttachInterrupt(T8, gotReset, threshold);         // GPIO 33
}

void handleModeTap() {
  unsigned long now = millis();

  if (now - lastModeTouchTime > cooldown) {
    tapCount++;
    lastTapTime = now;
    lastModeTouchTime = now;
  }
}

void resolveModeTaps() {
  unsigned long now = millis();

  if (tapCount > 0 && now - lastTapTime > tapWindow) {
    if (tapCount == 1) {
      Serial.println("MODE:PLANT");
    } else if (tapCount == 2) {
      Serial.println("MODE:WATER");
    } else if (tapCount >= 3) {
      Serial.println("MODE:CUT");
    }

    tapCount = 0;
  }
}

void loop() {
  unsigned long now = millis();

  // mode pad
  if (touchMode) {
    touchMode = false;
    handleModeTap();
  }
  resolveModeTaps();

  // reset pad
  if (touchReset && now - lastResetTime > cooldown) {
    touchReset = false;
    lastResetTime = now;
    Serial.println("RESET");
  } else if (touchReset) {
    touchReset = false;
  }

  // flower pads
  if (touchFrangipani && now - lastFrangipaniTime > cooldown) {
    touchFrangipani = false;
    lastFrangipaniTime = now;
    Serial.println("FLOWER:FRANGIPANI");
  } else if (touchFrangipani) {
    touchFrangipani = false;
  }

  if (touchDaisy && now - lastDaisyTime > cooldown) {
    touchDaisy = false;
    lastDaisyTime = now;
    Serial.println("FLOWER:DAISY");
  } else if (touchDaisy) {
    touchDaisy = false;
  }

  if (touchRose && now - lastRoseTime > cooldown) {
    touchRose = false;
    lastRoseTime = now;
    Serial.println("FLOWER:ROSE");
  } else if (touchRose) {
    touchRose = false;
  }

  if (touchTulip && now - lastTulipTime > cooldown) {
    touchTulip = false;
    lastTulipTime = now;
    Serial.println("FLOWER:TULIP");
  } else if (touchTulip) {
    touchTulip = false;
  }

  if (touchForgetMeNot && now - lastForgetMeNotTime > cooldown) {
    touchForgetMeNot = false;
    lastForgetMeNotTime = now;
    Serial.println("FLOWER:FORGET_ME_NOT");
  } else if (touchForgetMeNot) {
    touchForgetMeNot = false;
  }
}

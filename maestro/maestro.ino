#include <max6675.h>
#define RXD2 16
#define TXD2 17
#define RS485_EN 4

int pinSO  = 19;   // MISO (entrada) ✔
int pinCS  = 5;    // CS (salida) ✔
int pinSCK = 18;   // CLK (salida) ✔
MAX6675 termocupla(pinSCK, pinCS, pinSO);
unsigned long lastSend = 0;
String cmd="p";
char dato='p';
char h= '1';
char h_1='4';
int valorAntesS=1;
float temp_1=0;
void setup() {
  pinMode(RS485_EN, OUTPUT);
  digitalWrite(RS485_EN, LOW);  // Empezar en modo recepción

  Serial.begin(9600);         // Monitor serial USB
  Serial2.begin(38400, SERIAL_8N1, RXD2, TXD2);  // RS485
  Serial1.begin(9600, SERIAL_8N1, 26, 27);
}

void enviarComando(String msg) {
  digitalWrite(RS485_EN, HIGH);   // Transmitir
  delay(5);
  Serial2.print(msg);
  Serial2.flush();                // Esperar fin de envío
  digitalWrite(RS485_EN, LOW);    // Volver a recibir
  delay(5);
}
void loop() {
  if (Serial1.available()) {
    char c = Serial1.read();
    if(c!='\n'){
      dato = c;
      h = dato;
    }
  }
  if (Serial2.available()){
    cmd = Serial2.readStringUntil('\n');
    cmd.trim();
    if(cmd=="p")dato='p';
    if (cmd.length() > 1) {
      if (millis() - lastSend > 50) {  // enviar cada 0.5 s
        lastSend = millis();
        Serial1.println(cmd);
      }
   }
  }
  if(dato=='p'){
      float pot = analogRead(15);   // 20.0 – 30.0
      float temp = termocupla.readCelsius();
      if (isnan(temp)) {
        temp=temp_1;
      }else temp_1=temp;
      float s3 = 0.0;  // 15.0 – 25.0
      float s4 = 0;        // 1000 – 2000
      String cmd = String(pot, 2) + "___" +
             String(temp, 2) + "___" +
             String(s3, 2) + "___" +
             String(s4, 2);
    if (millis() - lastSend > 50) {  // enviar cada 0.5 s
      lastSend = millis();
      String tramaPC = cmd + "___M";
      Serial1.println(tramaPC);
      String com = tramaPC + "\n";
      enviarComando(com);
    }
  }
  if(dato=='R'){
    dato='1';
    enviarComando("p\n");
    
  }
}

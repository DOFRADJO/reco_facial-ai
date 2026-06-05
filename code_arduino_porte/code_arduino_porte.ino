/*
 * Code Arduino - Contrôle d'accès par Reconnaissance Faciale
 * 
 * Si "OPEN" est reçu : LED Verte, Message "Bienvenue", Buzzer (Aigu), Relais (Porte ouverte)
 * Si "DENY" est reçu : LED Rouge, Message "Non autorisé", Buzzer (Grave)
 */

const int RELAY_PIN = 7;      // Relais (Porte)
const int GREEN_LED_PIN = 6;  // LED Verte (Autorisé)
const int RED_LED_PIN = 5;    // LED Rouge (Refusé)
const int BUZZER_PIN = 4;     // Buzzer (Alarme/Signal)

void setup() {
  Serial.begin(9600);
  
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Tout est éteint par défaut
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(GREEN_LED_PIN, LOW);
  digitalWrite(RED_LED_PIN, LOW);
  
  Serial.println("Arduino pret. En attente du signal de la camera...");
}

void loop() {
  if (Serial.available() > 0) {
    String commande = Serial.readStringUntil('\n');
    commande.trim();
    
    if (commande == "OPEN") {
      // --- PERSONNE AUTORISÉE ---
      Serial.println("Bienvenue");
      
      digitalWrite(GREEN_LED_PIN, HIGH); // Allume LED Verte
      tone(BUZZER_PIN, 1000, 500);       // Bip aigu de 500ms
      digitalWrite(RELAY_PIN, HIGH);     // Ouvre la porte
      
      delay(5000);                       // Pause de 5 secondes
      
      digitalWrite(RELAY_PIN, LOW);      // Ferme la porte
      digitalWrite(GREEN_LED_PIN, LOW);  // Eteint LED Verte
      
    } 
    else if (commande == "DENY") {
      // --- PERSONNE NON AUTORISÉE ---
      Serial.println("Non autorise");
      
      digitalWrite(RED_LED_PIN, HIGH);   // Allume LED Rouge
      tone(BUZZER_PIN, 200, 1000);       // Bip grave de 1 seconde
      
      delay(3000);                       // Pause de 3 secondes
      
      digitalWrite(RED_LED_PIN, LOW);    // Eteint LED Rouge
    }
  }
}

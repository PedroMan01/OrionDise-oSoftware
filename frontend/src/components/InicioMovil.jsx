import { useEffect, useRef, useState } from "react";
import styles from './InicioMovil.module.css';

const InicioMovil = () => {
  return (
    <div className={styles.contenedor}>
      <a className={styles.boton} style={{backgroundColor: 'green'}} href="ChatVoz">Chat de voz</a>
      <a className={styles.boton} style={{backgroundColor: 'red'}} href="Chat">Chat</a>
      <a className={styles.boton} style={{backgroundColor: 'blue'}} href="Asistente">Asistente</a>
    </div>
  );
};

export default InicioMovil;
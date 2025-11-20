import { useEffect, useRef, useState } from "react";
import styles from './ChatMovil.module.css';

const ChatMovil = () => {
  return (
    <div className={styles.contenedor}>
      <a className={styles.boton} style={{backgroundColor: 'Orange'}} href="movil">Volver</a>
    </div>
  );
};

export default ChatMovil;
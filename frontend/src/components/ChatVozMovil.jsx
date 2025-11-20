import { useEffect, useRef, useState } from "react";
import styles from './ChatVozMovil.module.css';

const ChatVoz = () => {
  return (
    <div className={styles.contenedor}>
      <a className={styles.boton} style={{backgroundColor: 'Orange'}} href="movil">Volver</a>
    </div>
  );
};

export default ChatVoz;
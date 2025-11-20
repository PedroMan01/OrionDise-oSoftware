import { useEffect, useRef, useState } from "react";
import styles from './AsistenteMovil.module.css';

const AsistenteMovil = () => {
  return (
    <div className={styles.contenedor}>
      <a className={styles.boton} style={{backgroundColor: 'Orange'}} href="movil">Volver</a>
    </div>
  );
};

export default AsistenteMovil;
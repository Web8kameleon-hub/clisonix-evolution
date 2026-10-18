/**
 * EuroWeb - Loading Page
 * Pure CSS Modules + CVA + Framer Motion
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.0 Ultra
 */

import { LoadingSpinner } from '../components/LoadingSpinner'
import styles from './loading.module.css'

export default function Loading() {
  return (
    <div className={styles.container}>
      <LoadingSpinner size="large" />
      <p className={styles.text}>Loading EuroWeb Ultra Platform...</p>
    </div>
  )
}

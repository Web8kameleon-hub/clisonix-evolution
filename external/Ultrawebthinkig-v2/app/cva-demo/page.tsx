/**
 * EuroWeb - CVA Demo Page
 * Class Variance Authority Demo with CSS Modules
 */

import { cva } from 'class-variance-authority'
import styles from './page.module.css'

const buttonVariants = cva(
  styles.cvaButtonBase,
  {
    variants: {
      variant: {
        default: styles.cvaButtonDefault,
        secondary: styles.cvaButtonSecondary,
        outline: styles.cvaButtonOutline
      },
      size: {
        sm: styles.cvaButtonSm,
        md: styles.cvaButtonMd,
        lg: styles.cvaButtonLg
      }
    },
    defaultVariants: {
      variant: 'default',
      size: 'md'
    }
  }
)

export default function CVADemoPage() {
  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <h1 className={styles.title}>
          CVA Demo
        </h1>
        
        <p className={styles.subtitle}>
          Class Variance Authority - Type-safe CSS variants
        </p>
        
        <div className={styles.buttonGroup}>
          <button className={buttonVariants({ variant: 'default', size: 'sm' })}>
            Small Default
          </button>
          <button className={buttonVariants({ variant: 'secondary', size: 'md' })}>
            Medium Secondary
          </button>
          <button className={buttonVariants({ variant: 'outline', size: 'lg' })}>
            Large Outline
          </button>
        </div>
      </div>
    </div>
  )
}
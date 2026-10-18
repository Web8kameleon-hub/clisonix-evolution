/**
 * 🎨 STYLE PROPERTIES
 * Basic style properties për vanilla CSS dhe components
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0-STYLE-PROPS
 * @license MIT
 */

export interface BasicStyleProperties {
  // Spacing
  gap?: string | number;
  margin?: string | number;
  marginTop?: string | number;
  marginRight?: string | number;
  marginBottom?: string | number;
  marginLeft?: string | number;
  padding?: string | number;
  paddingTop?: string | number;
  paddingRight?: string | number;
  paddingBottom?: string | number;
  paddingLeft?: string | number;
  
  // Layout
  width?: string | number;
  height?: string | number;
  minWidth?: string | number;
  maxWidth?: string | number;
  minHeight?: string | number;
  maxHeight?: string | number;
  display?: string;
  position?: string;
  
  // Flexbox
  flexDirection?: string;
  justifyContent?: string;
  alignItems?: string;
  flexWrap?: string;
  
  // Grid
  gridTemplateColumns?: string;
  gridTemplateRows?: string;
  gridColumn?: string;
  gridRow?: string;
  
  // Typography
  fontSize?: string | number;
  fontFamily?: string;
  fontWeight?: string | number;
  lineHeight?: string | number;
  letterSpacing?: string | number;
  textAlign?: string;
  
  // Color
  color?: string;
  backgroundColor?: string;
  borderColor?: string;
  
  // Border
  border?: string;
  borderWidth?: string | number;
  borderStyle?: string;
  borderRadius?: string | number;
  
  // Effects
  boxShadow?: string;
  opacity?: number;
  transform?: string;
  transition?: string;
  
  // Responsive
  breakpoint?: string;
  responsive?: Record<string, any>;
}

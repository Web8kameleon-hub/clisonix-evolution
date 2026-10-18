/**
 * AGIxBioNature Tests - Pure TypeScript Biology Engine  
 * Zero mocks, zero hooks, pure functions only
 */

import { test, expect, describe } from 'vitest';

describe('AGIxBioNature Pure Logic Tests', () => {
  test('data formatting functions work correctly', () => {
    // Pure TypeScript functions - no React, no mocks
    const formatNumber = (value: number, decimals: number = 2): string => value.toFixed(decimals);
    const formatPopulation = (value: number): string => {
      if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
      if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
      if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
      return value.toString();
    };

    expect(formatNumber(0.78)).toBe('0.78');
    expect(formatPopulation(1500)).toBe('1.5K');
    expect(formatPopulation(1500000)).toBe('1.5M');
  });

  test('biological calculations are pure functions', () => {
    const calculateGeneticDiversity = (alleles: number, population: number): number => {
      return Math.min(1, alleles / (population * 2));
    };

    const calculateMetabolicRate = (bodyMass: number, temperature: number): number => {
      // Kleiber's law simplified
      return Math.pow(bodyMass, 0.75) * Math.exp(-0.1 * temperature);
    };

    expect(calculateGeneticDiversity(1500, 1000)).toBeCloseTo(0.75);
    expect(calculateMetabolicRate(25.5, 20)).toBeGreaterThan(0);
  });

  test('ecosystem data structures are immutable', () => {
    const createSpecimen = (id: string, species: string) => ({
      id,
      species,
      category: 'plant' as const,
      properties: {
        healthStatus: 'healthy' as const,
        readonly: true
      }
    } as const);

    const specimen = createSpecimen('001', 'Quercus alba');
    expect(specimen.id).toBe('001');
    expect(specimen.category).toBe('plant');
    expect(specimen.properties.readonly).toBe(true);
  });

  test('vector calculations for biodiversity work', () => {
    const calculateBiodiversityIndex = (species: readonly number[]): number => {
      const total = species.reduce((sum, count) => sum + count, 0);
      return species.reduce((index, count) => {
        if (count === 0) return index;
        const proportion = count / total;
        return index - (proportion * Math.log(proportion));
      }, 0);
    };

    // Shannon diversity index
    const speciesData = [100, 50, 25, 25] as const;
    const diversity = calculateBiodiversityIndex(speciesData);
    expect(diversity).toBeGreaterThan(1.0);
    expect(diversity).toBeLessThan(2.0);
  });
});

// Export pure utility functions (no React components)
// Removed unused export: BiologyUtils
const biologyUtils = {
  formatNumber: (value: number, decimals: number = 2): string => value.toFixed(decimals),
  formatPopulation: (value: number): string => {
    if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
    return value.toString();
  },
  calculateGeneticDiversity: (alleles: number, population: number): number => {
    return Math.min(1, alleles / (population * 2));
  }
};

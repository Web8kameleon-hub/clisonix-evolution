/**
 * Office Scripts Type Definitions
 * Për përdorim lokal në VS Code
 */

declare namespace ExcelScript {
    interface Workbook {
        getWorksheet(name: string): Worksheet | undefined;
        getActiveWorksheet(): Worksheet;
        getWorksheets(): Worksheet[];
    }

    interface Worksheet {
        getName(): string;
        getUsedRange(valuesOnly?: boolean): Range;
        getRange(address: string): Range;
        getCell(row: number, column: number): Range;
    }

    interface Range {
        getRowCount(): number;
        getColumnCount(): number;
        getValues(): (string | number | boolean | null)[][];
        getValue(): string | number | boolean | null;
        setValue(value: string | number | boolean): void;
        setValues(values: (string | number | boolean)[][]): void;
        getAddress(): string;
        getText(): string[][];
    }
}

import { expect, test } from 'vitest'
import { interpolateNumbers, coerceNumbersDeep } from '../../utils/math'


test('interpolate numbers should split the difference evenly', () => {
  expect(interpolateNumbers(0, 1)).toBe(0.5);
  expect(interpolateNumbers(16, 32)).toBe(24);
  expect(interpolateNumbers(-100, 50)).toBe(-25);
});
test('interpolate numbers should return the non-null number', () => {
  expect(interpolateNumbers(null, 99)).toBe(99);
  expect(interpolateNumbers(99, null)).toBe(99);
});
test('interpolate numbers should return the non-undefined number', () => {
  expect(interpolateNumbers(undefined, 99)).toBe(99);
  expect(interpolateNumbers(99, undefined)).toBe(99);
});
test('interpolate numbers should return unedfined when both inputs are null or undefined', () => {
  expect(interpolateNumbers(null, null)).toBe(undefined);
  expect(interpolateNumbers(undefined, undefined)).toBe(undefined);
  expect(interpolateNumbers(null, undefined)).toBe(undefined);
  expect(interpolateNumbers(undefined, null)).toBe(undefined);
});

test('coerce numbers deep should coerce strings, lists, and booleans', () => {
  expect(coerceNumbersDeep({"foo": "5.1"})).toStrictEqual({"foo": 5.1});
  expect(coerceNumbersDeep({"foo": [true, "2", "3"]})).toStrictEqual({"foo": [1, 2, 3]});
  expect(coerceNumbersDeep({"foo": true, "bar": false})).toStrictEqual({"foo": 1, "bar": 0});
});
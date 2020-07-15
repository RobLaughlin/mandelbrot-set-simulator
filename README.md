# Mandelbrot Set Simulator

This simulation uses Numpy to generate a 2D array of pixels mapped to points on the complex plane. These complex points are converted to RGB values where the color of each pixel states how far that complex number is in the recursive process of the Mandelbrot Set.

## Mandelbrot Set Recursive Definition
The Mandelbrot Set is defined as the set of all complex numbers that converge as the number of recursions (n) approach infinity.

![Mandelbrot Set Recursive Definition](README/img/mandelbrot_set_definition.svg)

It has been proven that if the absolute value of some complex number C is greater than 2 at any point in the recursive process, that complex number is divergent and not in the set. We use that very convenient fact in the program.

## Visual Example
![Mandelbrot Set Example Simulation](README/img/example_simulation.gif)

Notice how the color changes as we zoom into the set. Every black pixel is a complex number that is in the set, while every other pixel is colored somewhere farther on the color spectrum based on how many iterations it took before that complex number (pixel) began to diverge. 

Complex numbers colored orange took longer to diverge than complex numbers colored red, yellow longer than orange, green longer than yellow, etc, until the end of the spectrum (maximum recursions)

## Usage

To run the simulation,
```python
python main.py
```
Left-click to zoom in and right-click to zoom out.

## License
[GNU GPLv3](https://choosealicense.com/licenses/agpl-3.0/)
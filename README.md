# Hex Grid

This is an object-oriented refactor of 
[hexagonal grids](https://www.redblobgames.com/grids/hexagons/) by Amit Patel (@redblobgames). 

#### Dependencies

* Python 3.5+ because type hinting. Easy to clear if you need a lower version.

## Notes

* An edge is defined by the two hexes that share it, similarly a vertex by the three. 
This means that an edge or vertex around your grid's borders cannot be represented. Make sure you
 account for the extra "row" of hexes around your actual grid. 

* I skipped the few lines concerning hexagonal diagonals as I haven't felt a need for them. I 
might fix that in the future, or feel free to create a pull request. The original (unwrapped) 
code is simply commented out.

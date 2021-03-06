# Lava

A highlevel wrapper of Vulkan's compute API with numpy integration.

numpy + shaders = <3

### To-Do List
- [ ] memory alignment of (arbitrary) complex types
  - [x] scalars
    - [x] to shader
    - [x] from shader
  - [x] vectors
    - [x] to shader
    - [x] from shader
  - [x] matrices
    - [x] to shader
    - [x] from shader
  - [x] structures
    - [x] to shader
    - [x] from shader
  - [x] multi-dimensional arrays
    - [x] to shader
    - [x] from shader
  - [ ] dynamic length
- [ ] ~~images / samplers~~ (not for now)
- [ ] ~~push constants~~
- [x] bytecode analysis
  - [x] bindings
  - [x] local groups (?)
  - [x] misc (glsl version, entry point)
  - [x] parse type tree
- [ ] pipelines
  - [ ] oneshot
  - [ ] synchronization based on dependency graph
  - [ ] manual / automatic dependency dependency graph
  - [ ] gpu buffers/images (?)
- [x] highlevel interface
  - [x] session
  - [x] memory management (CPU / GPU, Buffer / Uniform ~~/ Image~~)
- [x] package
  - [x] pypi
  - [x] python3

### Diary

* 30.01.2019
  * ran into memory alignment issues with uniforms (matrix of type 2x2, 2x3, 2x4)
  * less/no problems with buffers **and** std430 layout (not available for uniforms) 
  * thinking about dropping support for uniforms (or just specific types?)
  * when dropping uniforms the std430 layout could be enforced to be used everywhere (what about images?)

* 01.02.2019
  * found usable documentation and understood the alignment and offset situation after all
  * works smoothly for scalars and vectors
  * arrays are probably next

* 02.02.2019
  * when overwriting (assigning it a second time) the first value of a dynamic output array in a ssbo it resets the entire array to 0
  * arrays for basic types (uint, int, float, double) is working (also special case with numpy array)

* 02.02.2019 (2)
  * wrote basic SPIR-V decoder
  * booleans seem to be stored as uints
  * bytecode also contains the variable names (are optional by spec, but I guess the vulkan glsl compiler always includes them)
  * basically all information from the bindings is stored in the bytecode (and can be used to check user input)
  * only thing missing is the layout (std140, std430)
 
* 07.02.2019
  * the bytecode contains offsets which can be used to check the offsets which are computed when transferring data to/from the gpu
  * this way the layout specified by the user can be confirmed
  * ideally the layout can be deduced at some point

* 15.02.2019
  * found a new bug introduced by that struct padding
  * apparently the padding is not necessary for arrays of structs? (see TestStructIn.test2)
  * ~~almost everything is in place to generically test the bytes implementations exhaustively (just testing tons of combinations for peace of mind)~~
  * iterating over multidimensional arrays is a reoccuring scheme, need to move that in a separete function/class/whatever

* 17.02.2019
  * I re-read the struct padding thingie and could resolve the bug
  * when adding a wiki / tutorial later there needs to be a chapter on matrices (numpy style is matrix[row][col], glsl style is matrix[col][row])
  * allowing to set the order for the matrix is not necessary as lava takes care about the alignment, I will try to force the user to use the default (COLUMN_MAJOR), proper integration would be annoying
  * lava shaders should set layout and order "globally for a block"

* 20.02.2019
  * my 1080 would take forever at vkCreateComputePipelines for shaders with large arrays (?)
  * only related stuff I could find was https://www.gamedev.net/forums/topic/686518-extreme-long-compile-times-and-bad-performance-on-nvidia/
  * I updated to nvidia's 415 driver (previously had 390) and now it works, phew

* 22.02.2019
  * dropping push constants
  * for flows to be usable each shader must declare readonly or writeonly access modifiers
  * buffers can have one of the following behaviours
    * unlimited read usages
    * _one_ write usage and unlimited usages _afterwards_

* 24.02.2019
  * doing some research on performance
  * access to ssbo's is indeed slow, in shader one should minimize the amount of reads and writes 

### Links

https://packaging.python.org/tutorials/packaging-projects/

https://python-future.org/compatible_idioms.html

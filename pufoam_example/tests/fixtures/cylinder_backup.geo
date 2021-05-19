radius = 1;
height = 1;
resolution = 10;

nodesHeight = height*resolution;
nodesCirc = 0.5*3.14*resolution;

Point(1) = {0,0,0};
Point(2) = {radius,0,0};
Point(3) = {0,radius,0};
Point(4) = {-radius,0,0};
Point(5) = {0,-radius,0};
  
Circle(1) = {2,1,3};
Circle(2) = {3,1,4};
Circle(3) = {4,1,5};
Circle(4) = {5,1,2};
Transfinite Line{1, 2, 3, 4} = nodesCirc; 
Line Loop(5) = {1,2,3,4};

Extrude {0,0,height} {Line{1, 2, 3, 4}; Layers{nodesHeight}; Recombine;}

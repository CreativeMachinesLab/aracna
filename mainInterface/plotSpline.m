%% plots a spline pp
function plotSpline(pp, n, x, y, clr, wdt, stl)
  if nargin < 7
    stl = '-';
  end
  % show the knots  
  plot(x,y, 'o', 'color', clr, 'linewidth', wdt);
  % visualize the spline
  sx = x(1):0.01:x(end); % controls the smoothness of visualization of the spline
  sy = ppval(pp, sx);
  plot(sx, sy, 'color', clr, 'linewidth', wdt, 'linestyle', stl); % Problem!! The spline might go
% outside [0,1] interval!!! maybe better to use DMP/attractors?? Or Gaussians?
end

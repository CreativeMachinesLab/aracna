function [pp2, x2, y2] = getNewSplineCyclic(pp, x, n2)
  %% get a new cyclic spline pp2, for a new number of spline knots n2,
  % replacing the old (also cyclic!) spline pp
  x2 = x(1+3) : (x(end-3)-x(1+3))/(n2-6-1):x(end-3); % x positions of knots
  y2 = ppval(pp, x2); % get the value of the old spline pp for the new knots x2
%  pp2 = spline(x2, y2);
  [pp2, x2, y2] = getCyclicSplinePlus6(x2, y2);
end

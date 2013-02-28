function [pp2, x2, y2, n2] = getCyclicSplinePlus6e(x, y) % NEW version 6e, can work even if there are only 3 knots!
  %% get a new spline pp2, which is cyclic, i.e. replaces y(n) with y(1) as last
  % knot and also adds 3 knots on each side to "wrap" cyclicly the spline
  % which makes sure the pos and pos dot at both ends match
  n = max(size(x));
  dx = x(2)-x(1);
  n2 = n+2*3; % new number of spline knots
  x2 = [ x(1)-3*dx  x(1)-2*dx  x(1)-dx  x(1:n-1)  x(n)  x(n)+dx  x(n)+2*dx  x(n)+3*dx ];
  if n == 3
  y2 = [ y(n-1)     y(n-2)     y(n-1)   y(1:n-1)  y(1)  y(2)     y(1)       y(2) ]; % replaces y(n) with y(1)
  elseif n > 3
  y2 = [ y(n-3)     y(n-2)     y(n-1)   y(1:n-1)  y(1)  y(2)     y(3)       y(4) ]; % replaces y(n) with y(1)
  else
    error('Unsupported number of knots n!')
  end;
  pp2 = spline(x2, y2); % calculate the spline  
end

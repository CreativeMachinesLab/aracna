function policy = paramToPolicy(param, policy)
  nbKnots = policy.s(1).n-3-3; % exclude the additional knots added for cyclicity of the spline
  nbPar = nbKnots - 1;
  for si=1:policy.n_splines
    % apply the new parameters from RL
    policy.s(si).y = [ param((si-1)*nbPar+1:si*nbPar)' param((si-1)*nbPar+1) ]; % y(n) = y(1)
    %    policy.pp = spline(policy.x, policy.y); % re-calculate the spline 
    % now turn it into a cyclic spline
    [policy.s(si).pp, policy.s(si).x, policy.s(si).y, policy.s(si).n] = getCyclicSplinePlus6e(policy.s(si).x(1+3:end-3), policy.s(si).y);
  end
end

function param = policyToParam(policy)
  param = [];
  for si=1:policy.n_splines
    param = [param ; policy.s(si).y(1+3:end-1-3)']; % excluding y(n) cause it's equal to y(1)
  end
end

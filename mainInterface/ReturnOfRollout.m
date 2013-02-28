function r = ReturnOfRollout(traj)
  %% Calculate the return (reward function) of a rollout
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

  % r = 0.456;
  % return;

  % maxHeight = max(traj(:,4))
  % r = maxHeight;
  % return

  % avgHeight = mean(traj(:,4))
  % r = exp(avgHeight);
  % return

  avgHeight = mean(traj(:,4))
  distTraveled = norm(traj(end,2:4) - traj(1,2:4)) % in [cm]
  duration = traj(end,1) - traj(1,1) % in [s]
  avgSpeed = distTraveled / duration % in [cm/s]

  r = avgSpeed;
%  r = (10*avgSpeed + avgHeight)^10; % combining speed and height
  return
end

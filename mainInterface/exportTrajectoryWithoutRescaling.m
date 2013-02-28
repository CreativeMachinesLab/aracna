function exportTrajectoryWithoutRescaling(policy, hFig, filepath);
  %% Export the produced trajectory to execute it on the robot
  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  % the policy contains: policy.pp, policy.x, policy.y, policy.n

  % timing
  total_duration = 12; % 12 sec total duration of walking
  cycle_duration = 1.8; % 1.3 sec period
  nbCycles = total_duration / cycle_duration;
  dt = 0.1; % 100 ms discretization step / control loop
  nbCycleSamples = cycle_duration / dt + 1;
  nbTotalSamples = total_duration / dt + 1;

  cycleTime = (0: dt: cycle_duration)';
  totalTime = (0: dt: total_duration)';

  % stretch the spline over the duration of one cycle
  for si=1:policy.n_splines
    s(si).XX = policy.s(si).x(1+3) : (policy.s(si).x(end-3)-policy.s(si).x(1+3))/(nbCycleSamples-1) : policy.s(si).x(end-3);
    s(si).YY = ppval(policy.s(si).pp, s(si).XX);
  end
  
  % rescale the trajectory y from [0,1] to stretch inside [zmin,zmax]
  posMin = 256;
  posMax = posMin + 512;
  posRange = posMax - posMin;
  for si=1:policy.n_splines
    % rescale
    s(si).cyclePos = s(si).YY .* posRange + posMin;
    s(si).cyclePos = s(si).cyclePos(:);
    % repeat cycle
    s(si).totalPos = [repmat(s(si).cyclePos(1:end-1), ceil(nbCycles), 1) ; s(si).cyclePos(end)]; % the last pos in a cycle is the same as the first pos in the next cycle
    s(si).totalPos = s(si).totalPos(1:nbTotalSamples); % the last cycle will probably be interrupted before its end
  end
  
  % plot the 'Exported trajectory' velocity and acceleration
  figure(hFig); clf; hold on; box on; grid on;
  clrmap = colormap(jet(policy.n_splines));
  for si=1:policy.n_splines
    plot(totalTime, s(si).totalPos, 'color', clrmap(si,:), 'linewidth', 2); % all cycles
    plot(cycleTime, s(si).cyclePos, 'color', clrmap(si,:), 'linewidth', 4); % just the first cycle is thicker, to highlight it
  end
  
  % Generate file input.txt for the simulator
  inputData = [];
  inputData = [inputData ; 0 512.0*ones(1, 9)]; % straight pose, fixed
  fixedPos = 512.0 * ones(nbTotalSamples, 1); % one column fixed value
  % individual joint's trajectories
  j(:,0+1) = s(1).totalPos; % fixedPos;
  j(:,1+1) = s(2).totalPos;
  j(:,2+1) = s(3).totalPos;
  j(:,3+1) = s(4).totalPos;
  j(:,4+1) = s(5).totalPos;
  j(:,5+1) = s(6).totalPos;
  j(:,6+1) = s(7).totalPos;
  j(:,7+1) = s(8).totalPos;
  j(:,8+1) = fixedPos;
  inputData = [inputData ; 2+totalTime, j(:,:)];

  % Export to a text file, for loading by the QuadraTot simulator
  dlmwrite([filepath '/input.txt'], '# Automatically generated file by Petar''s RL algorithm, containing joint trajectories for QuadraTot', 'delimiter', '');
  dlmwrite([filepath '/input.txt'], inputData , 'delimiter', ' ', '-append');

  % ---------------------------
  % #straight out pose
  % 2 512.0 512.0 512.0 512.0 512.0 512.0 512.0 512.0 512.0 0 0 0 0 0 0 0 0 0 0 0
  % #pose 1
  % 6 770.0 40.0 770.0 40.0 770.0 40.0 770.0 40.0 512.0 0 0 0 0 0 0 0 0 0 0 0
  % 12 770.0 40.0 770.0 40.0 770.0 40.0 770.0 40.0 512.0 0 0 0 0 0 0 0 0 0 0 0
  % #pose 2
  % 16 700.0 100.0 700.0 100.0 700.0 100.0 700.0 100.0 512.0 0 0 0 0 0 0 0 0 0 0 0
  % 20 700.0 100.0 700.0 100.0 700.0 100.0 700.0 100.0 512.0 0 0 0 0 0 0 0 0 0 0 0
  % #pose 3
  % 24 512.0 150.0 512.0 150.0 512.0 150.0 512.0 150.0 512.0 0 0 0 0 0 0 0 0 0 0 0
  % 28 512.0 150.0 512.0 150.0 512.0 150.0 512.0 150.0 512.0 0 0 0 0 0 0 0 0 0 0 0
  % #straight out
  % 32 512.0 512.0 512.0 512.0 512.0 512.0 512.0 512.0 512.0 0 0 0 0 0 0 0 0 0 0 0
  % ---------------------------
end

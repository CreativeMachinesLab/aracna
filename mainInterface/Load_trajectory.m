%% Load traj that the robot moved (returns matrix with 4 columns: t, x, y, z)
function traj = Load_trajectory(filename) % E.g. 'data/001/output_001.txt'
  hFig = figure('Name', '3D trajectory'); hold on; box on; grid on;

  % load electric current usage data
  data = dlmread(filename, '', 14, 0); % skip the first 13 lines
  traj = [data(:,1) data(:,20) data(:,22) data(:,21)]; % t, x, y, z

  plot3(traj(:,2), traj(:,3), traj(:,4), 'linewidth', 2);
  % plot traj starting pos
  plot3(traj(1,2), traj(1,3), traj(1,4),'.','markersize',20,'color',[0 1 0]);
  % plot traj end pos
  plot3(traj(end,2), traj(end,3), traj(end,4),'x','markersize',20,'color',[1 0 0]);

  view(3); axis equal;
  mn = min(min(traj(:,2:4)));
  mx = max(max(traj(:,2:4)));
  range = mx - mn;
  mn = mn - 0.1*range;
  mx = mx + 0.1*range;
  axis([mn mx mn mx mn mx]);
  xlabel('x'); ylabel('y'); zlabel('z');

  hFig = figure('Name', 'Individual axis trajectories', 'position', [1260, 200, 600, 900]); hold on; box on; grid on;
  subplot(3,1,1);
  disp('111');
  keyboard;
  plot(traj(:,1), traj(:,2), 'linewidth', 2);
  disp('222');
  xlabel('time'); ylabel('x');
  ylim([mn mx]);
  subplot(3,1,2);
  plot(traj(:,1), traj(:,3), 'linewidth', 2);
  xlabel('time'); ylabel('y');
  ylim([mn mx]);
  subplot(3,1,3);
  plot(traj(:,1), traj(:,4), 'linewidth', 2);
  xlabel('time'); ylabel('z');
  ylim([mn mx]);
end

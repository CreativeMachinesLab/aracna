function plotResults(hFig, n_rfs, variance, varianceLog, Return)
%% Plot
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
  figure(hFig);

  subplot(1,2,1);
  %figure('Name', 'Variance over rollouts'); hold on;
  for i=1:size(varianceLog,1)
      plot(varianceLog(i,:), 'color', [0 0 0]);
  end
  ylabel('variance');
  xlabel('rollouts');

  subplot(1,2,2);
  %figure('Name', 'Return over rollouts'); hold on;
  plot(Return);
  %axis([0 max(size(Return)) 0 1]);
  xlim([0 max(size(Return))]);
  ylabel('return');
  xlabel('rollouts');
end

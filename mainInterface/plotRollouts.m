function plotRollouts(hFig, n_iter, highlight_iter, policy, n_splines)
  %% plot all rollouts so far
  figure(hFig);
  clf; % clears the figure
  hold on;
  %    axis([-1 2 0 1]);
  xlim([-1 2]);

  clrmap = colormap(jet(n_splines));
  for iter=1:n_iter
    for si=1:n_splines
  %        clr = 'green';
          clr = clrmap(si,:);
          clr = (0.5 + 0.5*iter/n_iter) * clr; % gradient
          wdt = 2;
  %         if iter==highlight_iter % only for one
  %           wdt = 4;
  %           % clr = [1 0 0]; % red
  %         end
          plotSpline(policy(iter).s(si).pp, policy(iter).s(si).n, policy(iter).s(si).x, policy(iter).s(si).y, clr, wdt); % visualize the spline
    end
  end
  % plot the highlighted iteration last, to be on top of all others
  for si=1:n_splines
    wdt = 4;
    % clr = [1 0 0]; % red
    clr = clrmap(si,:);
    plotSpline(policy(highlight_iter).s(si).pp, policy(highlight_iter).s(si).n, policy(highlight_iter).s(si).x, policy(highlight_iter).s(si).y, clr, wdt); % visualize the spline
  end

  % draw vertical lines to mark a single time interval
  line([0 ; 0], [-0.1 ; 1.1], 'color', 'black', 'linewidth', 2);
  line([1 ; 1], [-0.1 ; 1.1], 'color', 'black', 'linewidth', 2);
end

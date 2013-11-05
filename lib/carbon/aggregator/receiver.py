from carbon.instrumentation import increment
from carbon.aggregator.rules import RuleManager
from carbon.aggregator.buffers import BufferManager
from carbon.rewrite import RewriteRuleManager
from carbon import events, log


def process(metric, datapoint):
  increment('datapointsReceived')

  for rule in RewriteRuleManager.preRules:
    metric = rule.apply(metric)

  aggregate_metrics = []

  for rule in RuleManager.rules:
    aggregate_metric = rule.get_aggregate_metric(metric)

    if aggregate_metric is None:
      continue
    else:
      aggregate_metrics.append(aggregate_metric)

    buffer = BufferManager.get_buffer(aggregate_metric)

    if not buffer.configured:
      buffer.configure_aggregation(rule.frequency, rule.aggregation_func)

    buffer.input(datapoint)

  for rule in RewriteRuleManager.postRules:
    metric = rule.apply(metric)

# TODO review how to configure forwarding of original event (on match/no-match)
  if not aggregate_metrics:
#### pass on unaggregated metric
    events.metricGenerated(metric, datapoint)
#  elif metric not in aggregate_metrics: 
####  prevent metric from overwriting aggregated metric
#    events.metricGenerated(metric, datapoint)

export interface SystemHealth {
  timestamp: string;
  overall_status: 'healthy' | 'degraded' | 'unhealthy';
  components: {
    database: ComponentStatus;
    classifier: ComponentStatus;
    recommender: ComponentStatus;
  };
  system_info: {
    cpu_usage_percent: number;
    memory: {
      total_gb: number;
      available_gb: number;
      used_percent: number;
    };
    disk: {
      total_gb: number;
      free_gb: number;
      used_percent: number;
    };
    python_version: string;
    platform: string;
  };
  warnings?: string[];
}

export interface ComponentStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  connection?: string;
  model_loaded?: boolean;
  model_type?: string;
  error?: string;
}

export interface ClassificationResult {
  text: string;
  primary_prediction: string;
  predictions: Array<{
    category: string;
    confidence: number;
    probability: number;
  }>;
  model_info: {
    model_type: string;
    algorithms: string[];
    feature_extraction: string;
    vocab_size?: number;
  };
}

export interface RecommendationResult {
  issue_text: string;
  total_recommendations: number;
  recommendations: Array<{
    rank: number;
    similarity_score: number;
    solution_id?: string;
    title: string;
    category?: string;
    solution_text: string;
    metadata?: {
      issue_type?: string;
      complexity?: string;
      estimated_time?: string;
      success_rate?: number;
      last_updated?: string;
      source?: string;
    };
    implementation_steps?: string[];
    prerequisites?: string[];
    potential_issues?: string[];
    verification_steps?: string[];
  }>;
  query_info: {
    top_k_requested: number;
    min_similarity: number;
    best_similarity: number;
    avg_similarity: number;
  };
}

export interface ParseResult {
  filename: string;
  file_type: string;
  parsing_successful: boolean;
  module_name?: string;
  baseline_version?: string;
  test_program_version?: string;
  test_results: any;
  error_count: number;
  warning_count: number;
  errors: Array<{
    message: string;
    line_number?: number;
    severity: string;
    timestamp?: string;
  }>;
  warnings: Array<{
    message: string;
    line_number?: number;
    severity: string;
    timestamp?: string;
  }>;
  execution_time?: number;
  memory_usage?: number;
  parsed_at: string;
  parsing_errors?: string[];
}

export interface UploadResult {
  total_files: number;
  successful_parses: number;
  failed_parses: number;
  results: ParseResult[];
  failed_files: Array<{
    filename: string;
    error: string;
  }>;
  summary: {
    total_errors: number;
    total_warnings: number;
    modules_processed: string[];
    baselines_processed: string[];
  };
}

export interface UsageStats {
  period: {
    start_date: string;
    end_date: string;
    days_analyzed: number;
  };
  total_requests: number;
  unique_users: number;
  avg_requests_per_day: number;
  peak_requests_per_hour: number;
  error_rate_percent: number;
  avg_response_time_ms: number;
  uptime_percent: number;
  endpoint_usage?: Array<{
    endpoint: string;
    requests: number;
    avg_response_time_ms: number;
    error_rate: number;
  }>;
  daily_usage?: Array<{
    date: string;
    requests: number;
    unique_users: number;
    errors: number;
  }>;
}

export interface PerformanceMetrics {
  analysis_period: {
    start_time: string;
    end_time: string;
    hours_analyzed: number;
  };
  overall_performance: {
    avg_response_time_ms: number;
    p50_response_time_ms: number;
    p95_response_time_ms: number;
    p99_response_time_ms: number;
    requests_per_second: number;
    error_rate_percent: number;
    success_rate_percent: number;
  };
  components?: {
    [key: string]: {
      avg_response_time_ms: number;
      p95_response_time_ms: number;
      [key: string]: any;
    };
  };
}

export interface IssueAnalytics {
  analysis_period: {
    start_date: string;
    end_date: string;
    days_analyzed: number;
  };
  summary: {
    total_issues_classified: number;
    unique_categories: number;
    avg_issues_per_day: number;
    most_common_category: string;
    classification_accuracy_estimate: number;
  };
  category_distribution: Record<string, number>;
  trends: {
    daily_counts: Array<{
      date: string;
      total_issues: number;
      top_category: string;
    }>;
  };
  confidence_metrics: {
    avg_confidence_score: number;
    high_confidence_rate: number;
    low_confidence_rate: number;
    confidence_distribution: Record<string, number>;
  };
}

export interface Solution {
  id: string;
  title: string;
  category: string;
  issue_type?: string;
  solution_preview: string;
  complexity: string;
  estimated_time?: string;
  success_rate?: number;
  last_updated?: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}

export interface NotificationData {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  duration?: number;
}

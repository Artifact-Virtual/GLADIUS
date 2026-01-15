/**
 * EnterpriseDatabase.js - Frontend service for enterprise database operations
 * 
 * Provides JavaScript interface for all enterprise database operations,
 * connecting React components to the enterprise_operations.db backend.
 */

class EnterpriseDatabase {
  constructor(baseUrl = 'http://localhost:5001') {
    this.baseUrl = baseUrl;
    this.apiEndpoint = `${baseUrl}/api/enterprise`;
  }

  // Generic API request method
  async apiRequest(endpoint, options = {}) {
    const url = `${this.apiEndpoint}${endpoint}`;
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`Enterprise Database API Error:`, error);
      throw error;
    }
  }

  // Business Objectives Operations
  async getBusinessObjectives() {
    return await this.apiRequest('/business-objectives');
  }

  async getBusinessObjectiveById(id) {
    return await this.apiRequest(`/business-objectives/${id}`);
  }

  async updateBusinessObjectiveProgress(id, progress) {
    return await this.apiRequest(`/business-objectives/${id}/progress`, {
      method: 'PUT',
      body: JSON.stringify({ progress })
    });
  }

  async createBusinessObjective(objective) {
    return await this.apiRequest('/business-objectives', {
      method: 'POST',
      body: JSON.stringify(objective)
    });
  }

  // Department Activities Operations
  async getDepartmentActivities() {
    return await this.apiRequest('/department-activities');
  }

  async getDepartmentActivitiesByDepartment(department) {
    return await this.apiRequest(`/department-activities/department/${department}`);
  }

  async updateActivityStatus(id, status) {
    return await this.apiRequest(`/department-activities/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    });
  }

  async createDepartmentActivity(activity) {
    return await this.apiRequest('/department-activities', {
      method: 'POST',
      body: JSON.stringify(activity)
    });
  }

  // Revenue Tracking Operations
  async getRevenueData() {
    return await this.apiRequest('/revenue');
  }

  async getRevenueByDateRange(startDate, endDate) {
    return await this.apiRequest(`/revenue/range?start=${startDate}&end=${endDate}`);
  }

  async updateRevenueActual(id, actualRevenue) {
    return await this.apiRequest(`/revenue/${id}/actual`, {
      method: 'PUT',
      body: JSON.stringify({ actual_revenue: actualRevenue })
    });
  }

  async createRevenueRecord(revenueData) {
    return await this.apiRequest('/revenue', {
      method: 'POST',
      body: JSON.stringify(revenueData)
    });
  }

  // Business Operations Tracking
  async getBusinessOperations() {
    return await this.apiRequest('/business-operations');
  }

  async getBusinessOperationsByType(operationType) {
    return await this.apiRequest(`/business-operations/type/${operationType}`);
  }

  async updateOperationStatus(id, status) {
    return await this.apiRequest(`/business-operations/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    });
  }

  async createBusinessOperation(operation) {
    return await this.apiRequest('/business-operations', {
      method: 'POST',
      body: JSON.stringify(operation)
    });
  }

  // Dashboard and Analytics
  async getDashboardSummary() {
    return await this.apiRequest('/dashboard/summary');
  }

  async getKPIMetrics() {
    return await this.apiRequest('/kpi/metrics');
  }

  async getTimelineData() {
    return await this.apiRequest('/timeline');
  }

  // Real-time data subscriptions
  async subscribeToUpdates(callback) {
    // WebSocket connection for real-time updates
    const wsUrl = `ws://localhost:5001/ws/enterprise`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Enterprise database WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        callback(data);
      } catch (error) {
        console.error('WebSocket message parse error:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('Enterprise database WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('Enterprise database WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(() => this.subscribeToUpdates(callback), 5000);
    };

    return ws;
  }
}

// Business Objectives Service
class BusinessObjectivesService {
  constructor(db) {
    this.db = db;
    this.cache = new Map();
    this.cacheTimeout = 30000; // 30 seconds
  }

  async getAll() {
    const cacheKey = 'all_objectives';
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const objectives = await this.db.getBusinessObjectives();
    this.cache.set(cacheKey, {
      data: objectives,
      timestamp: Date.now()
    });

    return objectives;
  }

  async getById(id) {
    const cacheKey = `objective_${id}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const objective = await this.db.getBusinessObjectiveById(id);
    this.cache.set(cacheKey, {
      data: objective,
      timestamp: Date.now()
    });

    return objective;
  }

  async updateProgress(id, progress) {
    const result = await this.db.updateBusinessObjectiveProgress(id, progress);
    
    // Invalidate cache
    this.cache.delete('all_objectives');
    this.cache.delete(`objective_${id}`);
    
    return result;
  }

  async getProgressSummary() {
    const objectives = await this.getAll();
    
    const summary = {
      total: objectives.length,
      completed: objectives.filter(obj => obj.progress >= 100).length,
      inProgress: objectives.filter(obj => obj.progress > 0 && obj.progress < 100).length,
      notStarted: objectives.filter(obj => obj.progress === 0).length,
      avgProgress: objectives.reduce((sum, obj) => sum + obj.progress, 0) / objectives.length
    };

    return summary;
  }

  clearCache() {
    this.cache.clear();
  }
}

// Department Activities Service
class DepartmentActivitiesService {
  constructor(db) {
    this.db = db;
    this.cache = new Map();
    this.cacheTimeout = 30000; // 30 seconds
  }

  async getAll() {
    const cacheKey = 'all_activities';
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const activities = await this.db.getDepartmentActivities();
    this.cache.set(cacheKey, {
      data: activities,
      timestamp: Date.now()
    });

    return activities;
  }

  async getByDepartment(department) {
    const cacheKey = `dept_${department}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const activities = await this.db.getDepartmentActivitiesByDepartment(department);
    this.cache.set(cacheKey, {
      data: activities,
      timestamp: Date.now()
    });

    return activities;
  }

  async updateStatus(id, status) {
    const result = await this.db.updateActivityStatus(id, status);
    
    // Invalidate relevant cache entries
    this.cache.delete('all_activities');
    
    return result;
  }

  async getDepartmentSummary() {
    const activities = await this.getAll();
    const departments = {};

    activities.forEach(activity => {
      if (!departments[activity.department]) {
        departments[activity.department] = {
          name: activity.department,
          total: 0,
          completed: 0,
          inProgress: 0,
          notStarted: 0,
          avgPriority: 0
        };
      }

      const dept = departments[activity.department];
      dept.total++;
      dept.avgPriority += activity.priority || 0;

      switch (activity.status) {
        case 'completed':
          dept.completed++;
          break;
        case 'in_progress':
          dept.inProgress++;
          break;
        case 'not_started':
          dept.notStarted++;
          break;
      }
    });

    // Calculate average priorities
    Object.values(departments).forEach(dept => {
      dept.avgPriority = dept.total > 0 ? dept.avgPriority / dept.total : 0;
    });

    return departments;
  }

  clearCache() {
    this.cache.clear();
  }
}

// Revenue Tracking Service
class RevenueTrackingService {
  constructor(db) {
    this.db = db;
    this.cache = new Map();
    this.cacheTimeout = 60000; // 1 minute for financial data
  }

  async getAll() {
    const cacheKey = 'all_revenue';
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const revenue = await this.db.getRevenueData();
    this.cache.set(cacheKey, {
      data: revenue,
      timestamp: Date.now()
    });

    return revenue;
  }

  async getByDateRange(startDate, endDate) {
    const cacheKey = `revenue_${startDate}_${endDate}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      return cached.data;
    }

    const revenue = await this.db.getRevenueByDateRange(startDate, endDate);
    this.cache.set(cacheKey, {
      data: revenue,
      timestamp: Date.now()
    });

    return revenue;
  }

  async updateActual(id, actualRevenue) {
    const result = await this.db.updateRevenueActual(id, actualRevenue);
    
    // Invalidate cache
    this.cache.clear();
    
    return result;
  }

  async getRevenueSummary() {
    const revenue = await this.getAll();
    
    const summary = {
      totalTarget: revenue.reduce((sum, r) => sum + (r.target_revenue || 0), 0),
      totalActual: revenue.reduce((sum, r) => sum + (r.actual_revenue || 0), 0),
      achievementRate: 0,
      monthlyData: [],
      currentMonthTarget: 0,
      currentMonthActual: 0
    };

    if (summary.totalTarget > 0) {
      summary.achievementRate = (summary.totalActual / summary.totalTarget) * 100;
    }

    // Group by month
    const monthlyGroups = {};
    revenue.forEach(r => {
      const monthKey = r.target_month;
      if (!monthlyGroups[monthKey]) {
        monthlyGroups[monthKey] = {
          month: monthKey,
          target: 0,
          actual: 0
        };
      }
      monthlyGroups[monthKey].target += r.target_revenue || 0;
      monthlyGroups[monthKey].actual += r.actual_revenue || 0;
    });

    summary.monthlyData = Object.values(monthlyGroups).sort((a, b) => 
      new Date(a.month) - new Date(b.month)
    );

    // Current month data
    const currentMonth = new Date().toISOString().slice(0, 7);
    const currentMonthData = monthlyGroups[currentMonth];
    if (currentMonthData) {
      summary.currentMonthTarget = currentMonthData.target;
      summary.currentMonthActual = currentMonthData.actual;
    }

    return summary;
  }

  clearCache() {
    this.cache.clear();
  }
}

// Export the class directly for instantiation
export default EnterpriseDatabase;

// Service instances can be created when needed
// export const businessObjectivesService = new BusinessObjectivesService(enterpriseDB);
// export const departmentActivitiesService = new DepartmentActivitiesService(enterpriseDB);
// export const revenueTrackingService = new RevenueTrackingService(enterpriseDB);

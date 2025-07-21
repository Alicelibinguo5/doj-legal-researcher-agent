import React from 'react';
import { TrendingUp, AlertTriangle, DollarSign, Users } from 'lucide-react';

const StatsCards = ({ results }) => {
  if (!results || results.length === 0) {
    return null;
  }

  // Calculate statistics
  const totalCases = results.length;
  
  // Count fraud cases
  const fraudCases = results.filter(case_ => {
    const gpt4o = case_.gpt4o;
    if (gpt4o && typeof gpt4o === 'object') {
      return gpt4o.fraud_flag === true;
    }
    const fraudInfo = case_.fraud_info;
    return fraudInfo && fraudInfo.is_fraud === true;
  }).length;

  // Count money laundering cases
  const launderingCases = results.filter(case_ => {
    const gpt4o = case_.gpt4o;
    if (gpt4o && typeof gpt4o === 'object') {
      return gpt4o.money_laundering_flag === true;
    }
    return case_.money_laundering_flag === true;
  }).length;

  // Count cases with both fraud and money laundering
  const bothCases = results.filter(case_ => {
    const gpt4o = case_.gpt4o;
    if (gpt4o && typeof gpt4o === 'object') {
      return gpt4o.fraud_flag === true && gpt4o.money_laundering_flag === true;
    }
    const fraudInfo = case_.fraud_info;
    return (fraudInfo && fraudInfo.is_fraud === true) && case_.money_laundering_flag === true;
  }).length;

  // Get unique URLs for fraud cases
  const fraudCaseUrls = new Set();
  results.forEach(case_ => {
    const gpt4o = case_.gpt4o;
    if (gpt4o && typeof gpt4o === 'object' && gpt4o.fraud_flag === true) {
      if (case_.url) fraudCaseUrls.add(case_.url);
    } else {
      const fraudInfo = case_.fraud_info;
      if (fraudInfo && fraudInfo.is_fraud === true && case_.url) {
        fraudCaseUrls.add(case_.url);
      }
    }
  });

  const uniqueFraudCases = fraudCaseUrls.size;

  const stats = [
    {
      title: 'Total Cases',
      value: totalCases,
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Fraud Cases',
      value: uniqueFraudCases,
      icon: AlertTriangle,
      color: 'text-red-600',
      bgColor: 'bg-red-50'
    },
    {
      title: 'Money Laundering',
      value: launderingCases,
      icon: DollarSign,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      title: 'Both Fraud & ML',
      value: bothCases,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => (
        <div key={index} className="stat-card">
          <div className={`inline-flex items-center justify-center w-12 h-12 rounded-lg ${stat.bgColor} mb-4`}>
            <stat.icon className={`w-6 h-6 ${stat.color}`} />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-1">{stat.value}</h3>
          <p className="text-sm text-gray-600">{stat.title}</p>
        </div>
      ))}
    </div>
  );
};

export default StatsCards; 
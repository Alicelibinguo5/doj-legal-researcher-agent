import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const ChargesChart = ({ results }) => {
  if (!results || results.length === 0) {
    return null;
  }

  // Extract all charges from results
  const allCharges = [];
  results.forEach(case_ => {
    if (case_.charges && Array.isArray(case_.charges)) {
      case_.charges.forEach(charge => {
        if (charge && typeof charge === 'string') {
          allCharges.push(charge.trim());
        }
      });
    }
  });

  // Count charge occurrences
  const chargeCounts = {};
  allCharges.forEach(charge => {
    chargeCounts[charge] = (chargeCounts[charge] || 0) + 1;
  });

  // Get top 10 charges
  const topCharges = Object.entries(chargeCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10)
    .map(([charge, count]) => ({
      charge: charge.length > 30 ? charge.substring(0, 30) + '...' : charge,
      count,
      fullCharge: charge
    }));

  if (topCharges.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Charges</h3>
        <p className="text-gray-600">No charges found in the results.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-6">Top Charges Distribution</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={topCharges} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="charge" 
              angle={-45}
              textAnchor="end"
              height={80}
              fontSize={12}
            />
            <YAxis fontSize={12} />
            <Tooltip 
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                      <p className="font-medium text-gray-900">{data.fullCharge}</p>
                      <p className="text-primary-600">Count: {data.count}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ChargesChart; 
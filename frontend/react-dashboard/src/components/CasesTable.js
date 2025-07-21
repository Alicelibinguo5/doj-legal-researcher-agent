import React, { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp, Filter, Download } from 'lucide-react';
import FeedbackWidget from './FeedbackWidget';

function toCSV(rows) {
  if (!rows || rows.length === 0) return '';
  const header = [
    'Title', 'Date', 'Fraud Flag', 'Money Laundering Flag', 'Fraud Category', 'Reasoning', 'Charges', 'URL'
  ];
  const csvRows = [header.join(',')];
  rows.forEach(row => {
    const gpt4o = row.gpt4o;
    const fraudInfo = row.fraud_info;
    const fraudFlag = gpt4o ? gpt4o.fraud_flag : (fraudInfo && fraudInfo.is_fraud);
    const launderingFlag = gpt4o ? gpt4o.money_laundering_flag : row.money_laundering_flag;
    const fraudCategory = gpt4o ? gpt4o.fraud_type : (fraudInfo ? (fraudInfo.charge_categories || []).join('; ') : '');
    const reasoning = gpt4o ? gpt4o.fraud_rationale : (fraudInfo && fraudInfo.evidence);
    const charges = (row.charges || []).join('; ');
    const url = row.url || '';
    csvRows.push([
      '"' + (row.title || '').replace(/"/g, '""') + '"',
      '"' + (row.date || '') + '"',
      fraudFlag ? 'Yes' : 'No',
      launderingFlag ? 'Yes' : 'No',
      '"' + (fraudCategory || '') + '"',
      '"' + (reasoning || '') + '"',
      '"' + charges + '"',
      '"' + url + '"'
    ].join(','));
  });
  return csvRows.join('\n');
}

const filterOptions = [
  { value: 'all', label: 'All Cases' },
  { value: 'fraud', label: 'Fraud Cases Only' },
  { value: 'non-fraud', label: 'Non-Fraud Cases Only' },
  { value: 'laundering', label: 'Money Laundering Only' },
  { value: 'non-laundering', label: 'Non-Laundering Only' },
];

const CasesTable = ({ results }) => {
  const [expandedRows, setExpandedRows] = useState(new Set());
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');

  if (!results || results.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Case Results</h3>
        <p className="text-gray-600">No cases found.</p>
      </div>
    );
  }

  const toggleRow = (index) => {
    const newExpanded = new Set(expandedRows);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedRows(newExpanded);
  };

  const getFraudFlag = (case_) => {
    const gpt4o = case_.gpt4o;
    if (gpt4o && typeof gpt4o === 'object') {
      return gpt4o.fraud_flag;
    }
    const fraudInfo = case_.fraud_info;
    return fraudInfo && fraudInfo.is_fraud;
  };

  const getMoneyLaunderingFlag = (case_) => {
    const gpt4o = case_.gpt4o;
    if (gpt4o && typeof gpt4o === 'object') {
      return gpt4o.money_laundering_flag;
    }
    return case_.money_laundering_flag;
  };

  const getFraudCategory = (case_) => {
    const gpt4o = case_.gpt4o;
    if (gpt4o && typeof gpt4o === 'object') {
      return gpt4o.fraud_type;
    }
    const fraudInfo = case_.fraud_info;
    return fraudInfo ? fraudInfo.charge_categories?.join(', ') : null;
  };

  const getReasoning = (case_) => {
    const gpt4o = case_.gpt4o;
    if (gpt4o && typeof gpt4o === 'object') {
      return gpt4o.fraud_rationale;
    }
    const fraudInfo = case_.fraud_info;
    return fraudInfo && fraudInfo.evidence;
  };

  // Filter and sort results
  let filteredResults = results.filter(case_ => {
    const fraudFlag = getFraudFlag(case_);
    const launderingFlag = getMoneyLaunderingFlag(case_);
    if (filter === 'fraud' && !fraudFlag) return false;
    if (filter === 'non-fraud' && fraudFlag) return false;
    if (filter === 'laundering' && !launderingFlag) return false;
    if (filter === 'non-laundering' && launderingFlag) return false;
    return true;
  });

  // Sort results
  filteredResults.sort((a, b) => {
    let aValue, bValue;
    
    switch (sortBy) {
      case 'date':
        aValue = new Date(a.date || '1900-01-01');
        bValue = new Date(b.date || '1900-01-01');
        break;
      case 'title':
        aValue = a.title || '';
        bValue = b.title || '';
        break;
      case 'fraud':
        aValue = getFraudFlag(a) ? 1 : 0;
        bValue = getFraudFlag(b) ? 1 : 0;
        break;
      default:
        aValue = a[sortBy] || '';
        bValue = b[sortBy] || '';
    }

    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const handleDownloadCSV = () => {
    const csv = toCSV(filteredResults);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'doj_research_results.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const SortIcon = ({ field }) => {
    if (sortBy !== field) return <ChevronDown className="w-4 h-4 text-gray-400" />;
    return sortOrder === 'asc' ? 
      <ChevronUp className="w-4 h-4 text-primary-600" /> : 
      <ChevronDown className="w-4 h-4 text-primary-600" />;
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Case Results ({filteredResults.length})</h3>
        <div className="flex items-center space-x-4">
          <button
            onClick={handleDownloadCSV}
            className="btn-secondary flex items-center space-x-2"
            title="Download CSV"
          >
            <Download className="w-4 h-4" />
            <span>Download CSV</span>
          </button>
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-500" />
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1"
            >
              {filterOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <button 
                  onClick={() => handleSort('title')}
                  className="flex items-center space-x-1 hover:text-gray-700"
                >
                  <span>Title</span>
                  <SortIcon field="title" />
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <button 
                  onClick={() => handleSort('date')}
                  className="flex items-center space-x-1 hover:text-gray-700"
                >
                  <span>Date</span>
                  <SortIcon field="date" />
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <button 
                  onClick={() => handleSort('fraud')}
                  className="flex items-center space-x-1 hover:text-gray-700"
                >
                  <span>Fraud</span>
                  <SortIcon field="fraud" />
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Money Laundering
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Article
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredResults.map((case_, index) => {
              const fraudFlag = getFraudFlag(case_);
              const launderingFlag = getMoneyLaunderingFlag(case_);
              const isExpanded = expandedRows.has(index);

              return (
                <React.Fragment key={index}>
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                        {case_.title || 'No Title'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {case_.date || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`badge ${fraudFlag ? 'badge-danger' : 'badge-success'}`}>
                        {fraudFlag ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`badge ${launderingFlag ? 'badge-warning' : 'badge-neutral'}`}>
                        {launderingFlag ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {case_.url ? (
                        <a
                          href={case_.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="btn-secondary text-primary-600 hover:underline"
                        >
                          Open
                        </a>
                      ) : (
                        <span className="text-gray-400">N/A</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => toggleRow(index)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                        {case_.url && (
                          <a
                            href={case_.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                  
                  {/* Expanded row with details */}
                  {isExpanded && (
                    <tr>
                      <td colSpan="6" className="px-6 py-4 bg-gray-50">
                        <div className="space-y-4">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <h4 className="font-medium text-gray-900 mb-2">Fraud Analysis</h4>
                              <div className="space-y-2 text-sm">
                                <div>
                                  <span className="font-medium">Category:</span> {getFraudCategory(case_) || 'N/A'}
                                </div>
                                <div>
                                  <span className="font-medium">Reasoning:</span> {getReasoning(case_) || 'N/A'}
                                </div>
                              </div>
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900 mb-2">Charges</h4>
                              <div className="text-sm">
                                {case_.charges && case_.charges.length > 0 ? (
                                  <ul className="list-disc list-inside space-y-1">
                                    {case_.charges.map((charge, i) => (
                                      <li key={i} className="text-gray-700">{charge}</li>
                                    ))}
                                  </ul>
                                ) : (
                                  <p className="text-gray-500">No charges listed</p>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          {/* Feedback Widget */}
                          <div className="border-t pt-4">
                            <h4 className="font-medium text-gray-900 mb-3">Help us improve</h4>
                            <FeedbackWidget 
                              caseData={case_}
                              onFeedbackSubmitted={(feedbackType, feedbackId) => {
                                console.log(`Feedback submitted for case ${index}: ${feedbackType} (ID: ${feedbackId})`);
                              }}
                            />
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CasesTable; 
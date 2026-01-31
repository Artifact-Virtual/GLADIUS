import { useState, useEffect } from 'react';
import { Package, Plus, Download, Trash2, Search, RefreshCw, Eye, FileText, Code, Database, Image, Archive, Filter, Upload, CheckCircle, AlertTriangle } from 'lucide-react';

interface Artifact {
  id: string;
  name: string;
  type: 'model' | 'dataset' | 'checkpoint' | 'config' | 'export' | 'log';
  size: string;
  created: Date;
  modified: Date;
  status: 'ready' | 'processing' | 'error';
  path: string;
  metadata?: Record<string, any>;
}

const ArtifactPage = () => {
  const [artifacts, setArtifacts] = useState<Artifact[]>([
    { id: '1', name: 'gladius1.1-71M.gguf', type: 'model', size: '142 MB', created: new Date(), modified: new Date(), status: 'ready', path: 'GLADIUS/models/native/' },
    { id: '2', name: 'checkpoint_epoch_50.pt', type: 'checkpoint', size: '284 MB', created: new Date(), modified: new Date(), status: 'ready', path: 'GLADIUS/checkpoints/' },
    { id: '3', name: 'training_data.jsonl', type: 'dataset', size: '1.2 GB', created: new Date(), modified: new Date(), status: 'ready', path: 'GLADIUS/data/' },
    { id: '4', name: 'config.json', type: 'config', size: '4 KB', created: new Date(), modified: new Date(), status: 'ready', path: 'config.json' },
    { id: '5', name: 'gladius1.1-71M-q4.gguf', type: 'export', size: '71 MB', created: new Date(), modified: new Date(), status: 'processing', path: 'GLADIUS/models/quantized/' },
    { id: '6', name: 'training_20240130.log', type: 'log', size: '12 MB', created: new Date(), modified: new Date(), status: 'ready', path: 'logs/' },
  ]);
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    loadArtifacts();
  }, []);

  const loadArtifacts = async () => {
    try {
      const result = await (window as any).electronAPI?.artifact?.list?.();
      if (result?.success && result?.data?.artifacts) {
        setArtifacts(result.data.artifacts);
      }
    } catch (error) {
      console.error('Failed to load artifacts:', error);
    }
  };

  const deleteArtifact = async (id: string) => {
    try {
      await (window as any).electronAPI?.artifact?.delete?.(id);
      setArtifacts(prev => prev.filter(a => a.id !== id));
      if (selectedArtifact?.id === id) setSelectedArtifact(null);
    } catch (error) {
      console.error('Failed to delete artifact:', error);
    }
  };

  const exportArtifact = async (artifact: Artifact) => {
    try {
      await (window as any).electronAPI?.artifact?.export?.(artifact.id, `exports/${artifact.name}`);
    } catch (error) {
      console.error('Failed to export artifact:', error);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'model': return <Database className="text-purple-400" size={20} />;
      case 'checkpoint': return <Archive className="text-blue-400" size={20} />;
      case 'dataset': return <FileText className="text-green-400" size={20} />;
      case 'config': return <Code className="text-yellow-400" size={20} />;
      case 'export': return <Package className="text-orange-400" size={20} />;
      case 'log': return <FileText className="text-gray-400" size={20} />;
      default: return <FileText className="text-gray-400" size={20} />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ready': return <span className="flex items-center gap-1 text-green-400 text-xs"><CheckCircle size={12} /> Ready</span>;
      case 'processing': return <span className="flex items-center gap-1 text-yellow-400 text-xs"><RefreshCw size={12} className="animate-spin" /> Processing</span>;
      case 'error': return <span className="flex items-center gap-1 text-red-400 text-xs"><AlertTriangle size={12} /> Error</span>;
      default: return null;
    }
  };

  const filteredArtifacts = artifacts.filter(a => {
    const matchesSearch = a.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === 'all' || a.type === filterType;
    return matchesSearch && matchesType;
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
            <Package className="text-accent" size={36} />
            Artifact Storage
          </h1>
          <p className="text-text-dim mt-2">Models, Checkpoints, Datasets & Exports</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={loadArtifacts}
            className="p-2 bg-primary/50 hover:bg-primary rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw size={20} />
          </button>
          <button
            onClick={() => setIsUploading(true)}
            className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg flex items-center gap-2 transition-colors"
          >
            <Upload size={18} />
            Upload
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card bg-gradient-to-br from-purple-500/10 to-transparent p-4">
          <Database className="text-purple-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Models</p>
          <p className="font-bold">{artifacts.filter(a => a.type === 'model').length}</p>
        </div>
        <div className="card bg-gradient-to-br from-blue-500/10 to-transparent p-4">
          <Archive className="text-blue-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Checkpoints</p>
          <p className="font-bold">{artifacts.filter(a => a.type === 'checkpoint').length}</p>
        </div>
        <div className="card bg-gradient-to-br from-green-500/10 to-transparent p-4">
          <FileText className="text-green-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Datasets</p>
          <p className="font-bold">{artifacts.filter(a => a.type === 'dataset').length}</p>
        </div>
        <div className="card bg-gradient-to-br from-orange-500/10 to-transparent p-4">
          <Package className="text-orange-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Total Size</p>
          <p className="font-bold">1.7 GB</p>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim" size={18} />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search artifacts..."
            className="w-full pl-10 pr-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent transition-colors"
          />
        </div>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent"
        >
          <option value="all">All Types</option>
          <option value="model">Models</option>
          <option value="checkpoint">Checkpoints</option>
          <option value="dataset">Datasets</option>
          <option value="config">Configs</option>
          <option value="export">Exports</option>
          <option value="log">Logs</option>
        </select>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Artifact List */}
        <div className="lg:col-span-2 card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="text-accent" size={20} />
            Artifact Registry ({filteredArtifacts.length})
          </h3>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {filteredArtifacts.map((artifact) => (
              <div 
                key={artifact.id}
                onClick={() => setSelectedArtifact(artifact)}
                className={`flex items-center justify-between p-4 rounded-lg cursor-pointer transition-all ${
                  selectedArtifact?.id === artifact.id 
                    ? 'bg-accent/20 border border-accent/50' 
                    : 'bg-primary/30 hover:bg-primary/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  {getTypeIcon(artifact.type)}
                  <div>
                    <p className="font-medium">{artifact.name}</p>
                    <p className="text-sm text-text-dim">{artifact.path}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-text-dim">{artifact.size}</span>
                  {getStatusBadge(artifact.status)}
                  <div className="flex gap-1">
                    <button
                      onClick={(e) => { e.stopPropagation(); exportArtifact(artifact); }}
                      className="p-1.5 bg-primary hover:bg-primary/80 rounded transition-colors"
                      title="Export"
                    >
                      <Download size={14} />
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); deleteArtifact(artifact.id); }}
                      className="p-1.5 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Artifact Details */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Eye className="text-accent" size={20} />
            Details
          </h3>
          
          {selectedArtifact ? (
            <div className="space-y-4">
              <div className="text-center py-4">
                <div className="w-16 h-16 mx-auto bg-primary/50 rounded-lg flex items-center justify-center mb-3">
                  {getTypeIcon(selectedArtifact.type)}
                </div>
                <h4 className="text-lg font-bold">{selectedArtifact.name}</h4>
                <span className="inline-block px-3 py-1 rounded mt-2 bg-primary text-text-dim text-sm capitalize">
                  {selectedArtifact.type}
                </span>
              </div>

              <div className="space-y-3">
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">Size</p>
                  <p className="font-medium">{selectedArtifact.size}</p>
                </div>
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">Path</p>
                  <p className="font-medium text-sm break-all">{selectedArtifact.path}</p>
                </div>
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">Created</p>
                  <p className="font-medium">{selectedArtifact.created.toLocaleString()}</p>
                </div>
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">Status</p>
                  {getStatusBadge(selectedArtifact.status)}
                </div>
              </div>

              <div className="flex gap-2 pt-4">
                <button 
                  onClick={() => exportArtifact(selectedArtifact)}
                  className="flex-1 py-2 bg-accent/20 hover:bg-accent/40 text-accent rounded-lg flex items-center justify-center gap-2"
                >
                  <Download size={16} />
                  Export
                </button>
                <button 
                  onClick={() => deleteArtifact(selectedArtifact.id)}
                  className="flex-1 py-2 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded-lg flex items-center justify-center gap-2"
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-text-dim">
              <Package className="mx-auto mb-3 opacity-50" size={48} />
              <p>Select an artifact to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ArtifactPage;

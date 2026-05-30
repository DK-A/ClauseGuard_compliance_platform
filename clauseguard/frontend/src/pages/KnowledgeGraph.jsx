import React, { useState, useEffect } from 'react';
import { Filter, Download, Maximize2, Share2, Layers, Shield } from 'lucide-react';
import ReactFlow, { MiniMap, Controls, Background, Handle, Position } from 'reactflow';
import 'reactflow/dist/style.css';

function CustomNode({ data, selected }) {
  return (
    <div 
      className={`p-4 rounded-2xl border bg-surface-container shadow-lg transition-all max-w-[280px] text-left relative ${
        selected ? 'ring-2 ring-primary/20' : 'hover:border-primary/50'
      }`}
      style={{ borderColor: selected ? 'var(--primary)' : data.color }}
    >
      <Handle 
        type="target" 
        position={Position.Top} 
        style={{ background: 'var(--primary)', width: '8px', height: '8px', border: '1.5px solid var(--surface)' }} 
      />
      
      <div className="flex items-center justify-between gap-3 mb-2 pb-1.5 border-b border-outline-variant/20">
        <span className="text-[9px] font-mono font-bold uppercase tracking-wider text-on-surface-variant max-w-[150px] truncate">
          {data.doc_source}
        </span>
        <span className={`text-[8px] font-headline font-bold uppercase px-1.5 py-0.5 rounded border ${
          data.clause_type === "prohibition" ? "bg-error/10 text-error border-error/20" :
          data.clause_type === "obligation" ? "bg-primary/10 text-primary border-primary/20" :
          "bg-tertiary-container/10 text-tertiary border-tertiary/20"
        }`}>
          {data.clause_type}
        </span>
      </div>
      
      <h5 className="font-headline text-[10px] font-bold text-on-surface mb-1 truncate">{data.label}</h5>
      <p className="text-[10px] text-on-surface-variant leading-relaxed line-clamp-3 select-text">
        "{data.text}"
      </p>

      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ background: 'var(--primary)', width: '8px', height: '8px', border: '1.5px solid var(--surface)' }} 
      />
    </div>
  );
}

const nodeTypes = {
  customNode: CustomNode,
};

export default function KnowledgeGraph({ activeSessionId }) {
  const [graph, setGraph] = useState({ nodes: [], edges: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterType, setFilterType] = useState("ALL");
  const [activeNeighbors, setActiveNeighbors] = useState([]);
  const [showOnlyConnected, setShowOnlyConnected] = useState(true);
  
  const refreshGraph = async () => {
    try {
      const { fetchGraphData } = await import('../api/client');
      const data = await fetchGraphData(activeSessionId);
      setGraph(data);
    } catch (e) {
      // standard fallback data set by client.js
    }
  };

  useEffect(() => {
    refreshGraph();
  }, [activeSessionId]);

  const handleNodeClick = (event, node) => {
    setSelectedNode(node);
    
    // Find all connected nodes (within 1-2 hops)
    const connected = [];
    graph.edges.forEach(edge => {
      if (edge.source === node.id) {
        connected.push(edge.target);
      } else if (edge.target === node.id) {
        connected.push(edge.source);
      }
    });
    setActiveNeighbors([node.id, ...connected]);
  };

  const handleCanvasClick = () => {
    setSelectedNode(null);
    setActiveNeighbors([]);
  };

  // Filter nodes & edges
  const filteredEdges = graph.edges.filter(edge => {
    if (filterType !== "ALL" && edge.label !== filterType) return false;
    
    // If select-focus mode is on, hide non-connected edges
    if (showOnlyConnected && selectedNode) {
      return edge.source === selectedNode.id || edge.target === selectedNode.id;
    }
    return true;
  });

  const filteredNodes = graph.nodes.map(node => {
    const isHighlighted = activeNeighbors.length === 0 || activeNeighbors.includes(node.id);
    let opacity = isHighlighted ? 1 : 0.20;
    
    // Hide completely (very low opacity, non-clickable) if selection focus is active and node is unrelated
    if (showOnlyConnected && selectedNode && !activeNeighbors.includes(node.id)) {
      opacity = 0.05;
    }
    
    return {
      ...node,
      style: {
        ...node.style,
        opacity: opacity,
        pointerEvents: opacity < 0.1 ? 'none' : 'auto'
      }
    };
  });

  return (
    <div className="h-[calc(100vh-80px)] w-full relative bg-background text-on-surface font-body animate-fadeIn overflow-hidden">
      {/* 1. Main Canvas Area */}
      <div className="w-full h-full relative" onClick={handleCanvasClick}>
        <ReactFlow
          nodes={filteredNodes}
          edges={filteredEdges}
          onNodeClick={handleNodeClick}
          nodeTypes={nodeTypes}
          fitView
          className="dot-grid"
        >
          <Controls className="bg-surface-container border border-outline-variant/30 text-on-surface rounded-xl p-1" />
          <Background color="#262932" gap={24} size={1} />
        </ReactFlow>

        {/* Legend Overlay (Bottom Left) */}
        <div className="absolute bottom-8 left-8 text-[11px] text-on-surface-variant space-y-1 z-30 pointer-events-none font-mono bg-surface-container/60 p-4 rounded-xl border border-outline-variant/20 backdrop-blur-md">
          <p>NODES: {graph.nodes.length}</p>
          <p>EDGES: {graph.edges.length}</p>
          <p>DENSITY: {(graph.edges.length / (graph.nodes.length * (graph.nodes.length - 1) || 1)).toFixed(2)}</p>
          <p className="text-primary mt-2">READY</p>
        </div>

        {/* Tier/View Switcher (Top Right) */}
        <div className="absolute top-8 right-8 flex flex-col space-y-3 z-30">
          {/* Edge Filter Panel */}
          <div className="bg-surface-container border border-outline-variant/30 rounded-2xl p-4 w-52 shadow-2xl backdrop-blur-md">
            <h4 className="text-[10px] font-headline text-on-surface-variant uppercase mb-3 tracking-wider font-bold">Layer Filters</h4>
            <div className="flex items-center justify-between text-xs py-2 px-1 border-b border-outline-variant/20 mb-3 pb-3">
              <span className="text-[9px] font-headline uppercase font-bold text-on-surface-variant">Focus Selected</span>
              <input 
                type="checkbox" 
                checked={showOnlyConnected} 
                onChange={(e) => setShowOnlyConnected(e.target.checked)}
                className="w-3.5 h-3.5 rounded text-primary border-outline-variant/40 bg-background focus:ring-primary cursor-pointer"
              />
            </div>
            <div className="space-y-3">
              <button 
                onClick={(e) => { e.stopPropagation(); setFilterType("ALL"); }}
                className={`w-full flex items-center justify-between text-xs py-1.5 px-3 rounded-lg transition-all ${
                  filterType === "ALL" ? "bg-primary/10 text-primary border border-primary/20 font-semibold" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                <span>Show All Edges</span>
                <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
              </button>

              <button 
                onClick={(e) => { e.stopPropagation(); setFilterType("DIRECT_CONTRADICTION"); }}
                className={`w-full flex items-center justify-between text-xs py-1.5 px-3 rounded-lg transition-all ${
                  filterType === "DIRECT_CONTRADICTION" ? "bg-error/10 text-error border border-error/20 font-semibold" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                <span>Contradictions</span>
                <span className="w-1.5 h-1.5 rounded-full bg-error"></span>
              </button>

              <button 
                onClick={(e) => { e.stopPropagation(); setFilterType("PARTIAL_OVERLAP"); }}
                className={`w-full flex items-center justify-between text-xs py-1.5 px-3 rounded-lg transition-all ${
                  filterType === "PARTIAL_OVERLAP" ? "bg-tertiary-container/25 text-tertiary border border-tertiary/20 font-semibold" : "text-on-surface-variant hover:text-on-surface"
                }`}
              >
                <span>Partial Overlap</span>
                <span className="w-1.5 h-1.5 rounded-full bg-tertiary"></span>
              </button>
            </div>

            <h4 className="text-[10px] font-headline text-on-surface-variant uppercase mb-2 mt-4 border-t border-outline-variant/20 pt-3 tracking-wider font-bold">Legend</h4>
            <div className="space-y-1.5 text-[9px] font-headline text-on-surface-variant">
              <div className="flex items-center gap-2"><span className="w-2.5 h-0.5 bg-[#ef4444]"></span><span>CONTRADICTS</span></div>
              <div className="flex items-center gap-2"><span className="w-2.5 h-0.5 bg-[#f59e0b]"></span><span>PARTIAL OVERLAP</span></div>
              <div className="flex items-center gap-2"><span className="w-2.5 h-0.5 bg-[#2563eb]"></span><span>SUPERSEDES</span></div>
            </div>
          </div>
        </div>

        {/* 2. Slide Node details Drawer (Bottom Right) */}
        {selectedNode && (
          <div 
            onClick={(e) => e.stopPropagation()} 
            className="absolute bottom-8 right-8 w-80 bg-surface-container border border-outline-variant/30 rounded-3xl p-6 shadow-2xl z-40 backdrop-blur-md animate-fadeIn"
          >
            <div className="flex items-center gap-2 mb-3">
              <span 
                className="w-2.5 h-2.5 rounded-full shrink-0" 
                style={{ backgroundColor: selectedNode.data.color }}
              ></span>
              <span className="font-headline text-[9px] uppercase tracking-widest font-bold text-on-surface-variant">
                {selectedNode.data.doc_source}
              </span>
            </div>
            <h4 className="text-sm font-bold text-on-surface mb-2">{selectedNode.data.label}</h4>
            <p className="text-xs text-on-surface-variant leading-relaxed mb-4">
              "{selectedNode.data.text}"
            </p>
            <div className="border-t border-outline-variant/20 pt-4 flex justify-between items-center">
              <span className="text-[10px] font-headline text-primary bg-primary/10 px-2.5 py-1 rounded uppercase tracking-wider font-bold">
                {selectedNode.data.clause_type}
              </span>
              <span className="text-[10px] text-on-surface-variant font-mono">ID: {selectedNode.id}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

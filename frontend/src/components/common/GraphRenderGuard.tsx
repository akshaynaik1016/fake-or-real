import {Component,type ReactNode} from 'react';
export class GraphRenderGuard extends Component<{children:ReactNode;onFailure?:()=>void;fallback?:ReactNode},{failed:boolean}>{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 componentDidCatch(){this.props.onFailure?.();}
 render(){return this.state.failed?this.props.fallback||<p role="alert" className="p-5 text-amber-200 text-sm">Graph visualization unavailable. All original evidence records remain in the list below.</p>:this.props.children;}
}
export function GraphFallbackRecords({nodes,onSelect}:{nodes:{id:string;type:string;label:string}[];onSelect:(id:string)=>void}){
 return <ul className="space-y-2 mt-2">{nodes.map(n=><li key={n.id}><button className="underline text-left" onClick={()=>onSelect(n.id)}>{n.type}: {n.label}</button></li>)}</ul>;
}

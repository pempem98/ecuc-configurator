"""
LDF (LIN Description File) loader.

Loads and parses LDF files for LIN network configuration.
"""

from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
import re

from .base_loader import BaseLoader, ParserError, ValidationError, ConversionError
from ..model import (
    LINNetwork, LINFrame, LINSignal, LINNode,
    LINNodeType, FrameType, ScheduleTable, ScheduleEntry
)


class LDFLoader(BaseLoader[LINNetwork]):
    """
    Loader for LDF (LIN Description File) files.
    
    Parses LDF format and converts to LINNetwork model.
    Note: This is a basic implementation. For production use, 
    consider using a dedicated LDF parser library.
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize LDF loader."""
        super().__init__(logger)
        self._content: str = ""
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Load and parse LDF file.
        
        Args:
            file_path: Path to LDF file
            
        Returns:
            Dictionary with parsed LIN network structure
            
        Raises:
            FileNotFoundError: If file does not exist
            ParserError: If LDF parsing fails
        """
        # Validate file exists and has correct extension
        path = self._validate_file_exists(file_path)
        self._validate_file_extension(path, ['.ldf', '.LDF'])
        
        try:
            # Read file content
            self.logger.info(f"Parsing LDF file: {path}")
            with path.open('r', encoding='utf-8') as f:
                self._content = f.read()
            
            # Parse LDF sections
            data = {
                'file_path': str(path),
                'header': self._parse_header(),
                'nodes': self._parse_nodes(),
                'signals': self._parse_signals(),
                'frames': self._parse_frames(),
                'schedule_tables': self._parse_schedule_tables(),
            }
            
            self.logger.info(
                f"Loaded {len(data['frames'])} frames, "
                f"{len(data['nodes'])} nodes, "
                f"{len(data['signals'])} signals"
            )
            
            return data
            
        except Exception as e:
            raise ParserError(f"Failed to parse LDF file: {e}") from e
    
    def _parse_header(self) -> Dict[str, str]:
        """Parse LDF header section."""
        header = {}
        
        # Parse LIN protocol version
        match = re.search(r'LIN_protocol_version\s*=\s*"([^"]+)"', self._content)
        if match:
            header['protocol_version'] = match.group(1)
        
        # Parse language version
        match = re.search(r'LIN_language_version\s*=\s*"([^"]+)"', self._content)
        if match:
            header['language_version'] = match.group(1)
        
        # Parse speed
        match = re.search(r'LIN_speed\s*=\s*([\d.]+)\s*kbps', self._content)
        if match:
            header['speed'] = float(match.group(1))
        
        return header
    
    def _parse_nodes(self) -> List[Dict[str, Any]]:
        """Parse nodes section."""
        nodes = []
        
        # Find Nodes section
        nodes_match = re.search(
            r'Nodes\s*\{([^}]+)\}',
            self._content,
            re.DOTALL
        )
        
        if not nodes_match:
            return nodes
        
        nodes_content = nodes_match.group(1)
        
        # Parse Master
        master_match = re.search(
            r'Master:\s*(\w+)',
            nodes_content
        )
        if master_match:
            nodes.append({
                'name': master_match.group(1),
                'type': 'master',
            })
        
        # Parse Slaves
        slaves_match = re.search(
            r'Slaves:\s*([^;]+);',
            nodes_content
        )
        if slaves_match:
            slave_names = slaves_match.group(1).split(',')
            for name in slave_names:
                name = name.strip()
                if name:
                    nodes.append({
                        'name': name,
                        'type': 'slave',
                    })
        
        return nodes
    
    def _parse_signals(self) -> List[Dict[str, Any]]:
        """Parse signals section."""
        signals = []
        
        # Find Signals section
        signals_match = re.search(
            r'Signals\s*\{([^}]+)\}',
            self._content,
            re.DOTALL
        )
        
        if not signals_match:
            return signals
        
        signals_content = signals_match.group(1)
        
        # Parse individual signals
        # Format: SignalName: size, init_value, Publisher, Subscriber1, Subscriber2;
        signal_pattern = r'(\w+):\s*(\d+)\s*,\s*(\d+)\s*,\s*(\w+)(?:\s*,\s*([^;]+))?;'
        
        for match in re.finditer(signal_pattern, signals_content):
            name = match.group(1)
            size = int(match.group(2))
            init_value = int(match.group(3))
            publisher = match.group(4)
            subscribers_str = match.group(5) if match.group(5) else ""
            
            subscribers = []
            if subscribers_str:
                subscribers = [s.strip() for s in subscribers_str.split(',') if s.strip()]
            
            signals.append({
                'name': name,
                'length': size,
                'initial_value': init_value,
                'publisher': publisher,
                'subscribers': subscribers,
            })
        
        return signals
    
    def _parse_frames(self) -> List[Dict[str, Any]]:
        """Parse frames section."""
        frames = []
        
        # Find Frames section
        frames_match = re.search(
            r'Frames\s*\{(.+?)\n\}',
            self._content,
            re.DOTALL
        )
        
        if not frames_match:
            return frames
        
        frames_content = frames_match.group(1)
        
        # Parse individual frames - more flexible pattern
        # Format: FrameName: id, Publisher, size { signal1, offset; signal2, offset; }
        # Split by frame definitions (looking for pattern: word: number)
        frame_pattern = r'(\w+):\s*(0x[\da-fA-F]+|\d+)\s*,\s*(\w+)\s*,\s*(\d+)\s*\{([^}]+)\}'
        
        for match in re.finditer(frame_pattern, frames_content, re.DOTALL):
            name = match.group(1)
            frame_id_str = match.group(2).strip()
            
            # Parse frame ID (can be decimal or hex)
            if frame_id_str.startswith('0x') or frame_id_str.startswith('0X'):
                frame_id = int(frame_id_str, 16)
            else:
                frame_id = int(frame_id_str)
            
            publisher = match.group(3).strip()
            length = int(match.group(4).strip())
            signals_str = match.group(5)
            
            # Parse signals in frame
            frame_signals = []
            # Remove comments and whitespace, split by semicolons
            signal_lines = [line.strip() for line in signals_str.split(';') if line.strip()]
            
            for sig_line in signal_lines:
                # Parse: SignalName, offset
                sig_match = re.match(r'(\w+)\s*,\s*(\d+)', sig_line.strip())
                if sig_match:
                    frame_signals.append({
                        'name': sig_match.group(1),
                        'offset': int(sig_match.group(2)),
                    })
            
            frames.append({
                'name': name,
                'frame_id': frame_id,
                'publisher': publisher,
                'length': length,
                'signals': frame_signals,
            })
        
        return frames
    
    def _parse_schedule_tables(self) -> List[Dict[str, Any]]:
        """Parse schedule tables section."""
        schedule_tables = []
        
        # Find Schedule_tables section
        schedule_match = re.search(
            r'Schedule_tables\s*\{(.+)\}',
            self._content,
            re.DOTALL
        )
        
        if not schedule_match:
            return schedule_tables
        
        schedule_content = schedule_match.group(1)
        
        # Parse individual schedule tables
        # Format: TableName { frame1 delay ms; frame2 delay ms; }
        table_pattern = r'(\w+)\s*\{([^}]+)\}'
        
        for match in re.finditer(table_pattern, schedule_content):
            table_name = match.group(1)
            entries_str = match.group(2)
            
            entries = []
            position = 0
            
            # Parse entries: FrameName delay ms;
            entry_pattern = r'(\w+)\s+delay\s+([\d.]+)\s*ms'
            
            for entry_match in re.finditer(entry_pattern, entries_str):
                frame_name = entry_match.group(1)
                delay = float(entry_match.group(2))
                
                entries.append({
                    'frame_name': frame_name,
                    'delay': delay,
                    'position': position,
                })
                position += 1
            
            schedule_tables.append({
                'name': table_name,
                'entries': entries,
            })
        
        return schedule_tables
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate parsed LDF data.
        
        Args:
            data: Parsed LDF data
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If validation fails
        """
        # Check required keys
        required_keys = ['header', 'nodes', 'signals', 'frames', 'schedule_tables']
        for key in required_keys:
            if key not in data:
                raise ValidationError(f"Missing required key: {key}")
        
        # Validate nodes
        if not isinstance(data['nodes'], list):
            raise ValidationError("'nodes' must be a list")
        
        # Validate at least one master node
        master_nodes = [n for n in data['nodes'] if n.get('type') == 'master']
        if not master_nodes:
            raise ValidationError("LIN network must have at least one master node")
        
        # Validate frames
        if not isinstance(data['frames'], list):
            raise ValidationError("'frames' must be a list")
        
        self.logger.debug("LDF data validation successful")
        return True
    
    def to_model(self, data: Dict[str, Any]) -> LINNetwork:
        """
        Convert parsed LDF data to LINNetwork model.
        
        Args:
            data: Validated LDF data
            
        Returns:
            LINNetwork model object
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            # Parse header info
            header = data.get('header', {})
            protocol_version = header.get('protocol_version', '2.1')
            language_version = header.get('language_version', '2.1')
            speed = header.get('speed', 19.2)
            
            # Convert signals
            signals_by_name = {}
            for sig_data in data['signals']:
                signal = LINSignal(
                    name=sig_data['name'],
                    short_name=sig_data['name'],
                    start_bit=0,  # Will be set by frame
                    length=sig_data['length'],
                    initial_value=sig_data.get('initial_value'),
                    publisher=sig_data.get('publisher'),
                    subscribers=sig_data.get('subscribers', []),
                )
                signals_by_name[sig_data['name']] = signal
            
            # Convert frames
            frames = []
            for frame_data in data['frames']:
                # Get signals for this frame
                frame_signals = []
                for sig_info in frame_data.get('signals', []):
                    sig_name = sig_info['name']
                    if sig_name in signals_by_name:
                        # Create a copy with updated start_bit
                        sig = signals_by_name[sig_name]
                        frame_signal = LINSignal(
                            name=sig.name,
                            short_name=sig.short_name,
                            start_bit=sig_info['offset'],
                            length=sig.length,
                            initial_value=sig.initial_value,
                            publisher=sig.publisher,
                            subscribers=sig.subscribers,
                        )
                        frame_signals.append(frame_signal)
                
                frame = LINFrame(
                    name=frame_data['name'],
                    short_name=frame_data['name'],
                    frame_id=frame_data['frame_id'],
                    length=frame_data['length'],
                    signals=frame_signals,
                    publisher=frame_data.get('publisher'),
                )
                frames.append(frame)
            
            # Convert nodes
            master_node = None
            slave_nodes = []
            
            for node_data in data['nodes']:
                node_type = LINNodeType.MASTER if node_data['type'] == 'master' else LINNodeType.SLAVE
                
                node = LINNode(
                    name=node_data['name'],
                    short_name=node_data['name'],
                    node_type=node_type,
                    protocol_version=protocol_version,
                )
                
                if node_type == LINNodeType.MASTER:
                    master_node = node
                else:
                    slave_nodes.append(node)
            
            # Convert schedule tables
            schedule_tables = []
            for table_data in data['schedule_tables']:
                entries = []
                for entry_data in table_data['entries']:
                    entry = ScheduleEntry(
                        name=f"{table_data['name']}_entry_{entry_data['position']}",
                        frame_name=entry_data['frame_name'],
                        delay=entry_data['delay'],
                        position=entry_data['position'],
                    )
                    entries.append(entry)
                
                schedule_table = ScheduleTable(
                    name=table_data['name'],
                    short_name=table_data['name'],
                    entries=entries,
                )
                schedule_tables.append(schedule_table)
            
            # Create network
            file_name = Path(data['file_path']).stem if 'file_path' in data else 'lin_network'
            network = LINNetwork(
                name=file_name,
                protocol_version=protocol_version,
                language_version=language_version,
                speed=speed,
                master_node=master_node,
                slave_nodes=slave_nodes,
                frames=frames,
                schedule_tables=schedule_tables,
            )
            
            self.logger.info(f"Converted to LINNetwork: {network.name}")
            return network
            
        except Exception as e:
            raise ConversionError(f"Failed to convert to model: {e}") from e

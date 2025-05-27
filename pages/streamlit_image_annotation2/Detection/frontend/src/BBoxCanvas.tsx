import React, { useState, useEffect, useRef } from "react"
import { Layer, Rect, Stage, Image } from 'react-konva';
import BBox from './BBox'
import Konva from 'konva';

export interface BBoxCanvasLayerProps {
  rectangles: any[],
  mode: string,
  selectedId: string | null,
  setSelectedId: any,
  setRectangles: any,
  setLabel: any,
  color_map: any,
  scale: number,
  label: string,
  image_size: number[],
  image: any,
  strokeWidth: number
}

const BBoxCanvas = (props: BBoxCanvasLayerProps) => {
  const {
    rectangles,
    mode,
    selectedId,
    setSelectedId,
    setRectangles,
    setLabel,
    color_map,
    scale,
    label,
    image_size,
    image,
    strokeWidth
  }: BBoxCanvasLayerProps = props

  const [adding, setAdding] = useState<number[] | null>(null)
  const [stageScale, setStageScale] = useState(1)
  const [stageX, setStageX] = useState(0)
  const [stageY, setStageY] = useState(0)
  const [showLabels, setShowLabels] = useState(true)
  const stageRef = useRef<Konva.Stage>(null)

  const SCALE_BY = 1.1
  const MIN_SCALE = 0.1
  const MAX_SCALE = 5

  const checkDeselect = (e: any) => {
    console.log('DOWN')
    if (!(e.target instanceof Konva.Rect)) {
      if (selectedId === null) {
        if (mode === 'Classificar') {
          const stage = e.target.getStage()
          const pointer = stage.getPointerPosition()
          if (!pointer) return
          // Adjust pointer position for stage transform
          const adjustedPointer = {
            x: (pointer.x - stageX) / stageScale,
            y: (pointer.y - stageY) / stageScale
          }
          setAdding([adjustedPointer.x, adjustedPointer.y, adjustedPointer.x, adjustedPointer.y])
        }
      } else {
        setSelectedId(null);
      }
    }
  };

  const handleWheel = (e: any) => {
    e.evt.preventDefault()

    const stage = stageRef.current
    if (!stage) return

    const oldScale = stageScale
    const pointer = stage.getPointerPosition()
    if (!pointer) return

    const mousePointTo = {
      x: (pointer.x - stageX) / oldScale,
      y: (pointer.y - stageY) / oldScale,
    }

    let direction = e.evt.deltaY > 0 ? -1 : 1
    
    // Reverse direction for natural zooming
    if (e.evt.ctrlKey) {
      direction = direction * -1
    }

    const newScale = direction > 0 ? oldScale * SCALE_BY : oldScale / SCALE_BY

    // Clamp scale
    const clampedScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, newScale))

    setStageScale(clampedScale)

    const newPos = {
      x: pointer.x - mousePointTo.x * clampedScale,
      y: pointer.y - mousePointTo.y * clampedScale,
    }

    setStageX(newPos.x)
    setStageY(newPos.y)
  }

  const resetZoom = () => {
    setStageScale(1)
    setStageX(0)
    setStageY(0)
  }

  const zoomIn = () => {
    const newScale = Math.min(MAX_SCALE, stageScale * SCALE_BY)
    setStageScale(newScale)
  }

  const zoomOut = () => {
    const newScale = Math.max(MIN_SCALE, stageScale / SCALE_BY)
    setStageScale(newScale)
  }

  const toggleLabels = () => {
    setShowLabels(!showLabels)
  }

  useEffect(() => {
    const rects = rectangles.slice();
    for (let i = 0; i < rects.length; i++) {
      if (rects[i].width < 0) {
        rects[i].width = rects[i].width * -1
        rects[i].x = rects[i].x - rects[i].width
        setRectangles(rects)
      }
      if (rects[i].height < 0) {
        rects[i].height = rects[i].height * -1
        rects[i].y = rects[i].y - rects[i].height
        setRectangles(rects)
      }
      if (rects[i].x < 0 || rects[i].y < 0) {
        rects[i].width = rects[i].width + Math.min(0, rects[i].x)
        rects[i].x = Math.max(0, rects[i].x)
        rects[i].height = rects[i].height + Math.min(0, rects[i].y)
        rects[i].y = Math.max(0, rects[i].y)
        setRectangles(rects)
      }
      if (rects[i].x + rects[i].width > image_size[0] || rects[i].y + rects[i].height > image_size[1]) {
        rects[i].width = Math.min(rects[i].width, image_size[0] - rects[i].x)
        rects[i].height = Math.min(rects[i].height, image_size[1] - rects[i].y)
        setRectangles(rects)
      }
      if (rects[i].width < 5 || rects[i].height < 5) {
        rects[i].width = 5
        rects[i].height = 5
      }
    }
    console.log(rects)
  }, [rectangles, image_size])

  return (
    <div>
      {/* Zoom Controls */}
      <div style={{ 
        position: 'absolute', 
        top: 10, 
        right: 5, 
        zIndex: 1000,
        display: 'flex',
        flexDirection: 'column',
        gap: '5px',
      }}>
        <button 
          onClick={toggleLabels}
          style={{
            padding: '8px 12px',
            backgroundColor: showLabels ? '#28a745' : '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            width: '90px'
          }}
        >
          {showLabels ? 'Hide Labels' : 'Show Labels'}
        </button>
        <button 
          onClick={resetZoom}
          style={{
            padding: '8px 12px',
            backgroundColor: '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            width: '90px'
          }}
        >
          Reset
        </button>
        <div style={{
          fontSize: '12px',
          color: '#666',
          textAlign: 'center'
        }}>
          {Math.round(stageScale * 100)}%
        </div>
      </div>

      <Stage 
        width={image_size[0] * scale} 
        height={image_size[1] * scale}
        ref={stageRef}
        scaleX={stageScale}
        scaleY={stageScale}
        x={stageX}
        y={stageY}
        onWheel={handleWheel}
        onMouseDown={checkDeselect}
        onMouseMove={(e: any) => {
          if (!(adding === null)) {
            const stage = e.target.getStage()
            const pointer = stage.getPointerPosition()
            if (!pointer) return
            // Adjust pointer position for stage transform
            const adjustedPointer = {
              x: (pointer.x - stageX) / stageScale,
              y: (pointer.y - stageY) / stageScale
            }
            setAdding([adding[0], adding[1], adjustedPointer.x, adjustedPointer.y])
          }
        }}
        onMouseLeave={(e: any) => {
          setAdding(null)
        }}
        onMouseUp={(e: any) => {
          if (!(adding === null)) {
            const rects = rectangles.slice();
            const new_id = Date.now().toString()
            rects.push({
              x: adding[0] / scale,
              y: adding[1] / scale,
              width: (adding[2] - adding[0]) / scale,
              height: (adding[3] - adding[1]) / scale,
              label: label,
              stroke: color_map[label],
              id: new_id
            })
            setRectangles(rects);
            setSelectedId(new_id);
            setAdding(null)
          }
        }}
      >
        <Layer>
          <Image image={image} scaleX={scale} scaleY={scale} />
        </Layer>
        <Layer>
          {rectangles.map((rect, i) => {
            return (
              <BBox
                key={i}
                rectProps={rect}
                scale={scale}
                strokeWidth={strokeWidth}
                showLabel={showLabels}
                isSelected={mode === 'Classificar' && rect.id === selectedId}
                onClick={() => {
                  if (mode === 'Classificar') {
                    setSelectedId(rect.id);
                    const rects = rectangles.slice();
                    const lastIndex = rects.length - 1;
                    const lastItem = rects[lastIndex];
                    rects[lastIndex] = rects[i];
                    rects[i] = lastItem;
                    setRectangles(rects);
                    setLabel(rect.label)
                  } else if (mode === 'Deletar') {
                    const rects = rectangles.slice();
                    setRectangles(rects.filter((element) => element.id !== rect.id));
                  }
                }}
                onChange={(newAttrs: any) => {
                  const rects = rectangles.slice();
                  rects[i] = newAttrs;
                  setRectangles(rects);
                }}
              />
            );
          })}
          {adding !== null && (
            <Rect 
              fill={color_map[label] + '4D'} 
              x={adding[0]} 
              y={adding[1]} 
              width={adding[2] - adding[0]} 
              height={adding[3] - adding[1]} 
            />
          )}
        </Layer>
      </Stage>
    </div>
  );
};

export default BBoxCanvas;
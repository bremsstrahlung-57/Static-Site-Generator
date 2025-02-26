class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props
        
    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if not self.props:
            return ""
        return " " + " ".join(f'{key}="{value}"' for key, value in self.props.items())       
        
    def __repr__(self):
        return f"HTMLNode(tag={self.tag}, value={self.value}, children={self.children}, props={self.props})"
    

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag, value=value, children=None,props=props)
        
    def to_html(self):
        if self.value is None or len(self.value) == 0:
            raise ValueError("LeafNode must have a non-empty value")
            
        if self.tag is None:
            return self.value
            
        props_str = self.props_to_html()
        return f"<{self.tag}{props_str}>{self.value}</{self.tag}>"
    
    
class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, value=None, children=children, props=props)
        
    def to_html(self):
        if self.tag is None or len(self.tag) == 0:
            raise ValueError("ParentNode must have a non-empty tag")
        if self.children is None or len(self.children) == 0:
            raise ValueError("ParentNode must have a children")

        body = "".join(x.to_html() for x in self.children)                
        return f"<{self.tag}>{"".join(body)}</{self.tag}>"
    
        